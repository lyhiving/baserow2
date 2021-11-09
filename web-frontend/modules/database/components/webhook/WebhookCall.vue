<template>
  <div class="webhook__call" :class="{ 'webhook__call--open': isExpanded }">
    <div class="webhook__call-head">
      <div class="webhook__call-name">
        <div class="webhook__call-type">{{ call.event_type }}</div>
        <div class="webhook__call-target">
          {{ call.called_url }}
        </div>
      </div>
      <div class="webhook__call-description">
        <div class="webhook__call-info">{{ lastCall }}</div>
        <a href="#" class="webhook__call-toggle" @click="toggleExpand()">
          <div class="webhook__call-state" :class="lastStatusClass">
            {{ statusDescription(call.status_code) }}
          </div>
          <i class="fas fa-chevron-down"></i>
        </a>
      </div>
    </div>
    <div class="webhook__call-body">
      <div class="webhook__call-body-content">
        <div class="webhook__call-body-label">{{ $t('webhook.request') }}</div>
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><code>{{ call.request }}</code></pre>
        </div>
      </div>
      <div class="webhook__call-body-content">
        <div class="webhook__call-body-label">{{ $t('webhook.response') }}</div>
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><code>{{ call.response }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import moment from '@baserow/modules/core/moment'
import webhook from '@baserow/modules/database/mixins/webhook'

export default {
  name: 'WebhookCall',
  mixins: [webhook],
  props: {
    call: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isExpanded: false,
    }
  },
  computed: {
    lastCall() {
      return moment(this.$props.call.called_time).format('YYYY-MM-DD HH:mm:ss')
    },
    lastStatusClass() {
      const statusCode = this.$props.call.status_code
      if (statusCode >= 200 && statusCode <= 299) {
        return 'webhook__head-call-state--ok'
      } else {
        return 'webhook__head-call-state--error'
      }
    },
  },
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>
