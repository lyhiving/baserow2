<template>
  <Modal :tiny="true">
    <div class="webhook__test-title">Test web hook</div>
    <div class="control">
      <div class="control__label">Request</div>
      <div class="control__elements">
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><code>{{request}}</code></pre>
        </div>
      </div>
    </div>
    <div class="control">
      <div class="control__label">Response</div>
      <div class="control__elements">
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><div v-if="isLoading" class="loading"></div><code v-if="!isLoading">{{response}}</code></pre>
        </div>
      </div>
    </div>
    <div class="webhook__test-state" :class="statusClass">
      {{ `${status} ${statusDescription}` }}
    </div>
    <div class="actions">
      <a href="#">Cancel</a>
      <div class="align-right">
        <button class="button button--ghost" @click="$emit('retry')">
          Retry
        </button>
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
  props: {
    request: {
      type: String,
      required: true,
    },
    response: {
      type: String,
      required: true,
    },
    status: {
      type: Number,
      required: true,
    },
    isLoading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    status200() {
      const status = this.$props.status
      if (status >= 200 && status <= 299) {
        return true
      } else {
        return false
      }
    },
    statusClass() {
      if (this.status200) {
        return 'webhook__test-state--ok'
      } else {
        return 'webhook__test-state--error'
      }
    },
    statusDescription() {
      if (this.status200) {
        return 'OK'
      } else {
        return 'NOT OK'
      }
    },
  },
  methods: {},
}
</script>
