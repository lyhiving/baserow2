<template>
  <form @submit.prevent="submit">
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">
            {{ $t('webhookForm.inputLabels.name') }}
          </label>
          <div class="control__elements">
            <input
              v-model="values.name"
              class="input"
              :class="{ 'input--error': $v.values.name.$error }"
            />
            <div v-if="$v.values.name.$error" class="error">
              {{ $t('error.requiredField') }}
            </div>
          </div>
        </div>
      </div>
      <div v-if="!create" class="col col-4">
        <div class="control">
          <label class="control__label">
            {{ $t('webhookForm.inputLabels.status') }}
          </label>
          <div class="control__elements">
            <Checkbox v-model="values.active">{{
              $t('webhookForm.checkbox.statusActive')
            }}</Checkbox>
          </div>
        </div>
      </div>
      <div class="col" :class="{ 'col-6': !create, 'col-12': create }">
        <div class="control">
          <label class="control__label">
            {{ $t('webhookForm.inputLabels.userFieldNames') }}
          </label>
          <div class="control__elements">
            <Checkbox v-model="values.use_user_field_names">{{
              values.use_user_field_names
                ? $t('webhookForm.checkbox.sendUserFieldNames')
                : $t('webhookForm.checkbox.sendFieldIDs')
            }}</Checkbox>
          </div>
        </div>
      </div>
      <div class="col col-4">
        <div class="control">
          <div class="control__label">
            {{ $t('webhookForm.inputLabels.requestMethod') }}
          </div>
          <div class="control__elements">
            <Dropdown v-model="values.request_method">
              <DropdownItem name="POST" value="POST"></DropdownItem>
              <DropdownItem name="GET" value="GET"></DropdownItem>
              <DropdownItem name="PATCH" value="PATCH"></DropdownItem>
              <DropdownItem name="PUT" value="PUT"></DropdownItem>
              <DropdownItem name="DELETE" value="DELETE"></DropdownItem>
            </Dropdown>
          </div>
        </div>
      </div>
      <div class="col col-8">
        <div class="control">
          <label class="control__label">
            {{ $t('webhookForm.inputLabels.url') }}
          </label>
          <div class="control__elements">
            <input
              v-model="values.url"
              class="input"
              :class="{ 'input--error': $v.values.url.$error }"
            />
            <div v-if="$v.values.url.$error" class="error">
              {{ $t('webhookForm.errors.urlField') }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="control">
      <label class="control__label">
        {{ $t('webhookForm.inputLabels.events') }}
      </label>
      <div class="control__elements">
        <Radio v-model="radio" value="all" @input="triggerAllEvents">{{
          $t('webhookForm.radio.allEvents')
        }}</Radio>
        <Radio v-model="radio" value="custom" @input="selectSingleEvent">
          {{ $t('webhookForm.radio.customEvents') }}
        </Radio>
        <div v-if="radio === 'custom'" class="webhook__types">
          <Checkbox v-model="events.rowCreated" class="webhook__type">{{
            $t('webhook.events.rowCreated')
          }}</Checkbox>
          <Checkbox v-model="events.rowUpdated" class="webhook__type">{{
            $t('webhook.events.rowUpdated')
          }}</Checkbox>
          <Checkbox v-model="events.rowDeleted" class="webhook__type">{{
            $t('webhook.events.rowDeleted')
          }}</Checkbox>
        </div>
      </div>
    </div>
    <div class="control">
      <div class="control__label">
        {{ $t('webhookForm.inputLabels.headers') }}
      </div>
      <div class="control__elements">
        <div
          v-for="(input, index) in defaultHeaders"
          :key="`headerInput-${index}`"
          class="webhook__header"
        >
          <div class="webhook__header-row">
            <input
              v-model="input.header"
              class="input webhook__header-key"
              :disabled="true"
            />
            <input
              v-model="input.value"
              class="input webhook__header-value"
              :disabled="true"
            />
          </div>
        </div>
        <div v-if="values.headers.length > 0">
          <div
            v-for="(input, index) in values.headers"
            :key="`headerInput-${index}`"
            class="webhook__header"
          >
            <div class="webhook__header-row">
              <input
                v-model="input.header"
                class="input webhook__header-key"
                placeholder="Header"
                @input="handleHeaderInputChange(index)"
              />
              <input
                v-model="input.value"
                class="input webhook__header-value"
                placeholder="Value"
                @input="handleHeaderInputChange(index)"
              />
              <a
                v-if="!lastHeaderElement(index)"
                href="#"
                class="button button--error webhook__header-delete"
                @click="removeHeaderField(index)"
              >
                <i class="fas fa-trash button__icon"></i>
              </a>
            </div>
          </div>
          <div v-if="areHeadersInvalid" class="webhook__header-row">
            <div class="error">
              {{ $t('webhookForm.errors.invalidHeaders') }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="control">
      <WebhookExample
        ref="webhookExample"
        :user-field-names="values.use_user_field_names"
      />
    </div>
    <a href="#" class="button button--ghost" @click="emitWebhookTrigger()">{{
      $t('webhookForm.triggerButton')
    }}</a>
    <slot></slot>
    <trigger-webhook-modal
      ref="triggerWebhookModal"
      :error="error"
      :request="trigger.request"
      :response="trigger.response"
      :status="trigger.status"
      :is-loading="trigger.isLoading"
      @retry="emitWebhookTrigger()"
      @cancel="cancelTriggerModal()"
    />
  </form>
</template>

<script>
import { required } from 'vuelidate/lib/validators'

import form from '@baserow/modules/core/mixins/form'
import error from '@baserow/modules/core/mixins/error'
import Checkbox from '@baserow/modules/core/components/Checkbox.vue'
import Radio from '@baserow/modules/core/components/Radio.vue'
import WebhookExample from './WebhookExample.vue'
import TriggerWebhookModal from './TriggerWebhookModal.vue'
import WebhookService from '@baserow/modules/database/services/webhook'

export default {
  name: 'WebhookForm',
  components: {
    Checkbox,
    Radio,
    WebhookExample,
    TriggerWebhookModal,
  },
  mixins: [form, error],
  props: {
    table: {
      type: Object,
      required: true,
    },
    create: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      allowedValues: [
        'name',
        'url',
        'request_method',
        'include_all_events',
        'use_user_field_names',
        'headers',
        'events',
        'active',
      ],
      values: {
        name: '',
        active: true,
        use_user_field_names: true,
        url: '',
        request_method: 'POST',
        headers: [{ header: '', value: '' }],
      },
      defaultHeaders: [{ header: 'Content-type', value: 'application/json' }],
      radio: 'all',
      events: {
        rowCreated: false,
        rowUpdated: false,
        rowDeleted: false,
      },
      eventsMapping: {
        rowCreated: 'row.created',
        rowUpdated: 'row.updated',
        rowDeleted: 'row.deleted',
      },
      trigger: {
        response: '',
        request: '',
        status: 0,
        isLoading: false,
      },
      areHeadersInvalid: false,
    }
  },
  created() {
    if (!this.$props.create) {
      if (this.defaultValues.include_all_events) {
        this.radio = 'all'
      } else {
        this.radio = 'custom'
        this.defaultValues.events.forEach((event) => {
          for (const [key, value] of Object.entries(this.eventsMapping)) {
            if (value === event.event_type) {
              this.events[key] = true
            }
          }
        })
      }
    }
  },
  validations: {
    values: {
      name: { required },
      url: { required },
    },
  },
  methods: {
    resetTriggerState() {
      this.trigger = {
        response: '',
        request: '',
        status: 0,
        isLoading: false,
      }
    },
    async emitWebhookTrigger() {
      // reset triggerState
      const selectedEvent = this.$refs.webhookExample.selectedEvent
      const eventType = this.eventsMapping[selectedEvent]
      this.resetTriggerState()
      this.hideError()
      this.trigger.isLoading = true
      const { id } = this.$props.table
      this.$v.$touch()
      const isFormValid = this.isFormValid()
      if (!isFormValid) {
        return
      }
      const formData = this.getFormValues()
      const requestObject = {
        event_type: eventType,
        webhook: formData,
      }
      this.$refs.triggerWebhookModal.show()
      try {
        const data = await WebhookService(this.$client).call(id, requestObject)
        this.trigger.isLoading = false
        const { request, response } = data.data
        const statusCode = data.data.status_code
        this.trigger.request = request
        this.trigger.response = response
        this.trigger.status = statusCode
      } catch (e) {
        this.trigger.isLoading = false
        this.handleError(e)
      }
    },
    cancelTriggerModal() {
      this.resetTriggerState()
      this.$refs.triggerWebhookModal.hide()
    },
    handleHeaderInputChange(index) {
      if (this.lastHeaderElement(index)) {
        this.addHeaderField()
      }
    },
    triggerAllEvents(val) {
      if (val) {
        this.showIndividualEvents = false
        this.resetSelectedEvents()
      }
    },
    selectSingleEvent(val) {
      if (val) {
        this.values.include_all_events = false
      }
    },
    resetSelectedEvents() {
      for (const [key] of Object.entries(this.events)) {
        this.events[key] = false
      }
    },
    addHeaderField() {
      this.values.headers.push({ header: '', value: '' })
    },
    removeHeaderField(index) {
      this.values.headers.splice(index, 1)
    },
    lastHeaderElement(index) {
      return index + 1 === this.values.headers.length
    },
    firstHeaderElement(index) {
      return index === 0
    },
    createEventsList() {
      const list = []
      for (const [key, value] of Object.entries(this.events)) {
        if (value) {
          list.push(this.eventsMapping[key])
        }
      }
      return list
    },
    validateHeaders() {
      // Check if there is a key-value pair where
      // the header is set but value is empty.
      this.resetHeaderError()
      this.values.headers.forEach((item, index) => {
        if (item.header.length > 0 && item.value.length < 2) {
          this.areHeadersInvalid = true
        }
      })
    },
    resetHeaderError() {
      this.areHeadersInvalid = false
    },
    getHeaderValues() {
      // remove empty headers and values
      const result = this.values.headers.filter((item) => {
        const bothNotEmpty = item.header !== '' && item.values !== ''
        const headerNotEmpty = item.header !== ''
        return bothNotEmpty || headerNotEmpty
      })
      return result
    },
    isFormValid() {
      this.validateHeaders()
      return !this.areHeadersInvalid && !this.$v.$invalid
    },
    getFormValues() {
      const headers = this.getHeaderValues()
      const valuesCopy = Object.assign({}, this.values)
      delete valuesCopy.events
      if (this.radio === 'custom') {
        const events = this.createEventsList()
        return { ...valuesCopy, include_all_events: false, events, headers }
      } else {
        return { ...valuesCopy, include_all_events: true, headers }
      }
    },
  },
}
</script>

<i18n>
{
  "en": {
    "webhookForm": {
      "inputLabels": {
        "name": "Name",
        "requestMethod": "Method",
        "url": "URL",
        "status": "Status",
        "userFieldNames": "User field names",
        "events": "Which events should trigger this webhook?",
        "headers": "Additional headers"
      },
      "errors": {
        "urlField": "This field is required and needs to be a valid url.",
        "invalidHeaders": "You cannot set a header without a value."
      },
      "checkbox": {
        "sendUserFieldNames": "Send user field names",
        "sendFieldIDs": "Send field ids",
        "statusActive": "Active"
      },
      "radio": {
        "allEvents": "Send me everything",
        "customEvents": "Let me select individual events"
      },
      "triggerButton": "Trigger test webhook"
    }
  },
  "fr": {
    "webhookForm": {
      "inputLabels": {
        "name": "@TODO",
        "requestMethod": "@TODO",
        "url": "@TODO",
        "status": "@TODO",
        "userFieldNames": "@TODO",
        "events": "@TODO",
        "headers": "@TODO"
      },
      "errors": {
        "urlField": "@TODO",
        "invalidHeaders": "@TODO"
      },
      "checkbox": {
        "sendUserFieldNames": "@TODO",
        "sendFieldIDs": "@TODO",
        "statusActive": "@TODO"
      },
      "radio": {
        "allEvents": "@TODO",
        "customEvents": "@TODO"
      },
      "triggerButton": "@TODO"
    }
  }
}
</i18n>
