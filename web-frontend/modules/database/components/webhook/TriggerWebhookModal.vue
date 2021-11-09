<template>
  <Modal :tiny="true">
    <div class="webhook__test-title">Test web hook</div>
    <Error :error="error" />
    <div v-if="isLoading" class="loading"></div>
    <div v-if="!isLoading">
      <div v-if="!error.visible" class="control">
        <div class="control__label">
          {{ $t('webhook.request') }}
        </div>
        <div class="control__elements">
          <div class="webhook__code-container">
            <pre
              class="webhook__code webhook__code--small"
            ><code>{{request}}</code></pre>
          </div>
        </div>
      </div>
      <div v-if="status" class="control">
        <div class="control__label">
          {{ $t('webhook.response') }}
        </div>
        <div class="control__elements">
          <div class="webhook__code-container">
            <pre
              class="webhook__code webhook__code--small"
            ><div v-if="isLoading" class="loading"></div><code v-if="!isLoading">{{response}}</code></pre>
          </div>
        </div>
      </div>
      <div
        v-if="!error.visible"
        class="webhook__test-state"
        :class="statusClass"
      >
        {{ statusString(status) }}
      </div>
      <div class="actions">
        <a href="#" @click="$emit('cancel')">{{ $t('action.cancel') }}</a>
        <div class="align-right">
          <button class="button button--ghost" @click="$emit('retry')">
            {{ $t('action.retry') }}
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script>
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'
import webhook from '@baserow/modules/database/mixins/webhook'

export default {
  name: 'TriggerWebhookModal',
  mixins: [modal, error, webhook],
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
      required: false,
      default: null,
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
  },
  methods: {
    statusString(statusCode) {
      if (!statusCode) {
        return 'Server unreachable'
      }
      return this.statusDescription(statusCode)
    },
  },
}
</script>

<i18n>
{
  "en": {
    "triggerWebhookModal": {
      "title": "Test webhook"
    }
  },
  "fr": {
    "triggerWebhookModal": {
      "title": "@TODO"
    }
  }
}
</i18n>
