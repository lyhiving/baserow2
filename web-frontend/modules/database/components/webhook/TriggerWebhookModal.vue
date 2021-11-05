<template>
  <Modal :tiny="true">
    <div class="webhook__test-title">Test web hook</div>
    <div class="control">
      <div class="control__label">Request</div>
      <div class="control__elements">
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><code>POST https://target-url.com/target-page
Authorization: Some token
Content-Type: application/json

{
    “id”: 1,
    “type”: “row_deleted”,
    “old_values”: {}
}</code></pre>
        </div>
      </div>
    </div>
    <div class="control">
      <div class="control__label">Response</div>
      <div class="control__elements">
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><div class="loading"></div></pre>
        </div>
      </div>
    </div>
    <div class="webhook__test-state webhook__test-state--error">
      404 NOT FOUND
    </div>
    <div class="actions">
      <a href="#">Cancel</a>
      <div class="align-right">
        <button class="button button--ghost">Retry</button>
      </div>
    </div>
  </Modal>
</template>

<script>
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'TriggerWebhookModal',
  mixins: [modal, error],
  data() {
    return {
      loading: false,
    }
  },
  methods: {},
}
</script>
