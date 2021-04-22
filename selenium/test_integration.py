import os
import subprocess
import uuid

import atexit
import pytest
import requests
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from urllib3.util.retry import Retry
import pathlib


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# the ENVS env variable is a comma separated list which controls which ENVS are started
# in this test.
ENVS_VAR = os.environ.get("ENVS", "all")
EXPANDED_ENVS = "local,dev,saas" if ENVS_VAR == "all" else ENVS_VAR
ENVS = EXPANDED_ENVS.split(",")


def bash(bash_command, cwd="."):
    """
    Runs a bash command in a sub folder and the provided cwd directory. Will stream
    the sub processes stderr and stdout back to the test process so you can see
    what is happening in real time.
    """
    print(f"Running Bash: {bash_command}")

    def stream_process(p):
        go = p.poll() is None
        for line in p.stdout:
            print(line.decode("utf-8"), end="")
        return go

    process = subprocess.Popen(
        bash_command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    while stream_process(process):
        sleep(0.1)
    retval = process.poll()
    assert retval == 0
    return


already_downed = {}


@pytest.fixture(scope="function")
def local_env():
    yield from start_env("local", "docker-compose -f docker-compose.yml ")


@pytest.fixture(scope="function")
def dev_env():
    yield from start_env("dev", "./dev.sh dont_attach")


@pytest.fixture(scope="function")
def saas_env():
    yield from start_env(
        "saas",
        "./dev.sh dont_attach -f docker-compose.yml ",
        cwd="../../../../baserow-saas",
        backend_port="8001",
    )


def start_env(env, prefix, cwd="../", backend_port="8000"):
    """
    Uses bash subprocesses to start up the provided environment, check it's backend is
    healthy before starting the test and clean up appropriately afterwards.
    """
    if env not in ENVS:
        yield "skip"
        return
    build = os.environ.get("BUILD", "on") == "on"
    cleanup = os.environ.get("CLEANUP", "on") == "on" or len(ENVS) > 1

    path_to_test_folder = pathlib.Path(__file__).parent
    prefix += (
        f" -f {path_to_test_folder.absolute()}/docker-compose.integration-test.yml "
    )
    env_location = path_to_test_folder.joinpath(cwd)
    if not env_location.is_dir():
        if env != "saas":
            raise Exception(
                f"Could not find {env} env, looking in "
                f"{env_location.absolute()} and it is not a directory."
            )
        else:
            # Auto skip saas as it is a private env
            yield "skip"
            return

    def cleanup_docker_containers():
        global already_downed
        if env not in already_downed and cleanup:
            print("Test cleaning up:")
            bash(f"{prefix} down", cwd=cwd)
            bash(f"{prefix} rm", cwd=cwd)
            already_downed[env] = True

    atexit.register(cleanup_docker_containers)
    if build:
        bash(f"{prefix} build", cwd=cwd)
    if cleanup:
        bash(f"{prefix} down", cwd=cwd)
    bash(
        f"EMAIL_SMTP_HOST=fake-smtp-server "
        f"EMAIL_SMTP_PORT=1025 "
        f"EMAIL_SMTP=True "
        f"{prefix} "
        f"up -d "
        f"--remove-orphans",
        cwd=cwd,
    )
    request_session = wait_for_backend_to_be_healthy(backend_port)
    reset_emails()
    yield request_session
    cleanup_docker_containers()


def wait_for_backend_to_be_healthy(backend_port):
    request_session = requests.Session()
    retries = Retry(total=10, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    request_session.mount("http://", HTTPAdapter(max_retries=retries))
    api_url = f"http://localhost:{backend_port}/"
    health_check = api_url + "_health"
    assert request_session.get(health_check)
    return request_session


@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()


def test_dev_env(dev_env, driver):
    if dev_env == "skip":
        return
    driver.get("http://localhost:3000/")
    WebDriverWait(driver, 120).until_not(EC.title_is("Nuxt.js: Loading app..."))
    run_baserow_core_tests(driver)


def test_local_env(local_env, driver):
    if local_env == "skip":
        return
    run_baserow_core_tests(driver)


def test_saas_env(saas_env, driver):
    if saas_env == "skip":
        return
    driver.get("http://localhost:3001/login")
    WebDriverWait(driver, 120).until_not(EC.title_is("Nuxt.js: Loading app..."))
    run_baserow_core_tests(driver, "http://localhost:3001/login")
    assert_no_broken_links_on_entire_site(driver, "http://localhost:3001")


def run_baserow_core_tests(driver, login_address="http://localhost:3000/"):
    """
    A core set of tests that should work in every baserow env. Designed so we check
    every sub-system integration point works. (Redis, Celery, File uploads,
    Email sending, General site behaviour, Nuxt and the Backend)
    """
    driver.get(login_address)
    username, email, password = sign_up_new_user(driver)
    assert_on_dashboard(driver, username)
    assert_can_create_file_field_and_upload_working_image_via_url(driver)
    assert_can_open_second_window_and_see_changes_in_real_time(
        driver, email, password, login_address
    )
    assert_can_logoff_and_get_sent_reset_password_email(driver, email)


def get_emails():
    """
    We are running a fake smtp server injected via docker-compose.integration-test.yml
    This endpoint will return any emails it has recieved since it was last started up
    or reset.
    """
    emails_response = requests.get("http://localhost:1080/api/emails")
    emails_response.raise_for_status()
    r = emails_response.json()
    return r


def reset_emails():
    """
    Resets the fake stmp server's email log.
    """
    emails_response = requests.delete("http://localhost:1080/api/emails")
    emails_response.raise_for_status()


def assert_can_logoff_and_get_sent_reset_password_email(
    driver,
    email,
):
    """
    Logs off the user and clicks through to send a reset password email, then checks
    that an actual smtp email was really sent to our fake smtp server.
    """
    assert len(get_emails()) == 0
    # Logoff using the sidebar menu
    sidebar_user = driver.find_element_by_class_name("sidebar__user")
    actions = ActionChains(driver)
    actions.move_to_element(sidebar_user).click().perform()
    driver.find_element_by_link_text("Logoff").click()
    # Wait until we have logged off
    WebDriverWait(driver, 10).until(EC.title_is("Login // Baserow"))
    # Go to the forget the password page, fill in our email in and submit
    driver.find_element_by_link_text("Forgot password").click()
    email_input = driver.find_element_by_xpath("//input[1]")
    email_input.send_keys(email, Keys.ENTER)
    # Wait for the confirmation that the email has been sent
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, "box__message-text"),
            "If your email address exists in our database",
        )
    )
    # Check the fake smtp server email log that it recieved an email
    retries = 0
    while len(get_emails()) != 1 and retries < 5:
        sleep(1)
        retries += 1
    assert len(get_emails()) == 1, (
        "The fake smtp server did not recieve any emails, "
        "is email sending via smtp broken?"
    )


def login_user(driver, email, password):
    """
    Fills in email and password in the form and then submits
    Assumes we are on the login page already
    """
    email_input = driver.find_element_by_xpath("//input[1]")
    email_input.send_keys(email)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB)
    actions.send_keys(password, Keys.ENTER)
    actions.perform()


def assert_can_open_second_window_and_see_changes_in_real_time(
    driver, email, password, login_address
):
    """
    Opens a second selenium window, modifies a cell in the project tracker table and
    asserts that both windows see the change. This checks that the realtime websocket
    updates going via django channels and redis are working correctly.
    """
    second_window = webdriver.Firefox()
    try:
        # Login the second window
        second_window.get(login_address)
        login_user(second_window, email, password)
        # Switch to the Project Tracker project
        project_tracker_xpath = "//span[text()='Project Tracker']/.."
        WebDriverWait(second_window, 10).until(
            EC.element_to_be_clickable((By.XPATH, project_tracker_xpath))
        )
        # Switch to the Projects table
        project_link = second_window.find_element_by_xpath(project_tracker_xpath)
        actions = ActionChains(second_window)
        actions.move_to_element(project_link).click().perform()
        second_window.find_element_by_link_text("Projects").click()
        # Wait for the table to be loaded
        WebDriverWait(second_window, 10).until(
            EC.title_is("All projects - Projects // Baserow")
        )
        # Check the cells match between the two windows before we do anything
        cell_search = "grid-field-text"
        cell_in_first_window = driver.find_element_by_class_name(cell_search)
        cell_in_second_window = second_window.find_element_by_class_name(cell_search)
        assert cell_in_first_window.text == cell_in_second_window.text
        # Double click the cell, clear it, input new data and enter it all in the second
        # window
        action_chains = ActionChains(second_window)
        action_chains.double_click(cell_in_second_window).perform()
        input_box = second_window.find_element_by_css_selector(".active > " "input")
        input_box.clear()
        input_box.send_keys("New Cell Data", Keys.ENTER)
        # Confirm that the cell has changed its data in both windows
        WebDriverWait(second_window, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "(//div[@class='grid-field-text'])[1]"), "New Cell Data"
            )
        )
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "(//div[@class='grid-field-text'])[1]"), "New Cell Data"
            )
        )
    finally:
        second_window.quit()


def assert_can_create_file_field_and_upload_working_image_via_url(driver):
    """
    Creates a project from a template, navigates to a table in the project, adds a
    file column, uploads an image from a link, clicks the uploaded file and confirms
    no images are broken and that the env is correctly serving uploaded files
    """
    # Create a project from a template
    driver.find_element_by_link_text("Create new").click()
    driver.find_element_by_link_text("From template").click()
    driver.find_element_by_link_text("Use this template").click()
    # Wait until it has loaded
    WebDriverWait(driver, 10).until(EC.title_is("All projects - Projects // Baserow"))
    # Add a new file field
    driver.find_element_by_class_name("grid-view__add-column").click()
    name = driver.find_element_by_xpath("//input[@placeholder='Name']")
    name.send_keys("Test File Field")
    driver.find_element_by_link_text("Make a choice").click()
    driver.find_element_by_link_text("File").click()
    driver.find_element_by_xpath('//button[normalize-space()="Create"]').click()
    # Click into the file fields first cell and upload a file via an url
    driver.find_element_by_class_name("grid-field-file__cell").click()
    driver.find_element_by_class_name("grid-field-file__item-add").click()
    driver.find_element_by_link_text("a URL").click()
    url_input = driver.find_element_by_xpath("//input[1]")
    i = (
        "https://www.google.com/images/branding/googlelogo/1x/"
        "googlelogo_color_272x92dp.png"
    )
    url_input.send_keys(i)
    header = driver.find_element_by_xpath('//*[text()="Upload from a URL"]')
    driver.find_element_by_xpath('//button[normalize-space()="Upload"]').click()
    # Wait for the file upload modal to disappear
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(header))
    # TODO: Bug we need to click to refresh the cell after uploading a file!
    driver.find_element_by_class_name("grid-field-file__cell").click()
    # Click on the uploaded file
    wait_for_element_with_class_name(driver, "grid-field-file__link").click()
    # Make sure the env is serving uploaded files correctly
    assert_no_broken_images(driver)
    # Close the modal
    wait_for_element_with_class_name(driver, "file-field-modal__close").click()


def wait_for_element_with_class_name(driver, classname):
    return WebDriverWait(driver, 1000).until(
        EC.presence_of_element_located((By.CLASS_NAME, classname))
    )


def assert_no_broken_images(driver):
    """
    Checks every image on the current page that we can request them and they return a
    200 response.
    """
    image_list = driver.find_elements(By.TAG_NAME, "img")

    broken_image_count = 0
    for img in image_list:
        response = requests.get(img.get_attribute("src"), stream=True)
        if response.status_code != 200:
            print(img.get_attribute("outerHTML") + " is broken.")
            broken_image_count = broken_image_count + 1
    assert broken_image_count == 0


def assert_no_broken_links_on_entire_site(driver, base_url, log_output=True):
    """
    Slow check which is disabled by default and can be enabled with CHECKLINKS=on.
    Crawls the entire SAAS site checking on every page that all the links work and
    return a 200 response. Ignores some types of links which we expect to be broken.
    Also ignores email links. It checks external links work but does not navigate to
    them to continue crawling.
    """
    if os.environ.get("CHECK_LINKS", "off") != "on":
        print(
            f"{bcolors.WARNING}Skipping saas links check, enable with "
            f"CHECK_LINKS=on{bcolors.ENDC}"
        )
        return

    # The list of pages we still need to visit to crawl
    pending = []
    # The pages we have already visited so we dont revisit
    visited = set()
    # The pages we have requested already and don't need to do a get request for
    checked = set()
    # Urls we expect to be broken and its not an error
    url_ignores = {
        "http://localhost:3000/",
        "https://localhost:3001/",
        "http://localhost:3001/example",
        "http://localhost:8000/style-guide",
        "http://localhost:8000/api/redoc",
        "http://localhost:8000/api/redoc/",
        # As expected returns a no cred link, the docs explicitly tell you this will
        # happen
        "http://localhost:8001/api/groups/",
        "http://localhost:8000/api/groups/",
        "http://localhost:8001/api/my-baserow-plugin/example/",
    }
    # All of the external links found on the SAAS site
    external_links = []
    # Any broken links
    broken_links = []

    driver.get(base_url)
    while True:
        # Every loop we:
        # 1. Find all the a links on the current page
        # 2. Send get requests to every new valid link checking they respond with a 200
        # 3. Any internal links found which we have not yet visited get added to the
        #    pending list
        # 4. Pop the next page to visit off the pending list and continue the crawl
        link_list = driver.find_elements(By.TAG_NAME, "a")
        visited.add(driver.current_url)
        checked.add(driver.current_url)

        for link in link_list:
            url = link.get_attribute("href")
            if not url:
                continue
            email = url.startswith("mailto:")
            assert url.startswith("http") or email, f"{url} was " f"weird"
            if email:
                if log_output:
                    print(f"Skipping email link: {url}")
                continue

            if url.startswith(base_url):
                external = False
            else:
                external = True
            if url not in checked and url not in url_ignores:
                checked.add(url)
                # Dont bother following anchor links
                if "#" not in url:
                    if log_output:
                        print(f"requesting {url}")
                    # noinspection PyBroadException
                    try:
                        response = requests.get(url)
                        if response.status_code != 200:
                            if log_output:
                                print(f"BROKEN Status: {url}")
                            broken_links.append(f"{url} {response.status_code}")
                        else:
                            if external:
                                external_links.append(url)
                            else:
                                pending.append(url)
                    except Exception:
                        if log_output:
                            print(f"BROKEN Exception: {url}")
                        broken_links.append(f"{url}")

        if len(pending) == 0:
            break
        else:
            pop = pending.pop()
            if log_output:
                print(f"Checking {pop}")
            # noinspection PyBroadException
            try:
                driver.get(pop)
            except Exception:
                if log_output:
                    print("Invalid for driver")
                broken_links.append(pop + " - driver")

    if log_output:
        print(f"EXTERNAL LINKS: {external_links}")
    assert broken_links == []


def assert_on_dashboard(driver, username):
    WebDriverWait(driver, 10).until(EC.title_is("Dashboard // Baserow"))
    EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, "dashboard__group-title > span"),
        f"{username}'s group",
    )


def sign_up_new_user(driver):
    """
    Expects we are on the login page and signs up a new user. Generates them an email
    address using a uid so multiple test runs over the same DB dont collide.
    """
    sign_up_link = driver.find_element_by_link_text("Sign up")
    sign_up_link.click()
    uid = str(uuid.uuid4())[:8]
    email_address = uid + "@example.com"
    email_input = driver.find_element_by_xpath("//input[1]")
    email_input.send_keys(email_address)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB)
    name = "SELENIUM TEST USER " + uid
    actions.send_keys(name, Keys.TAB)
    password = "testpassword"
    actions.send_keys(password, Keys.TAB)
    actions.send_keys(password, Keys.ENTER)
    actions.perform()
    return name, email_address, password
