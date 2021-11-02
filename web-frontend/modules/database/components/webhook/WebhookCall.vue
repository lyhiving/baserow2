<template>
  <div class="webhook__call" :class="{ 'webhook__call--open': isExpanded }">
    <div class="webhook__call-head">
      <div class="webhook__call-name">
        <div class="webhook__call-type">Row created</div>
        <div class="webhook__call-target">
          {{ call.called_url }}
        </div>
      </div>
      <div class="webhook__call-description">
        <div class="webhook__call-info">{{ call.called_time }}</div>
        <a href="#" class="webhook__call-toggle" @click="toggleExpand()">
          <div class="webhook__call-state webhook__head-call-state--ok">
            {{ call.status_code }}
          </div>
          <i class="fas fa-chevron-down"></i>
        </a>
      </div>
    </div>
    <div class="webhook__call-body">
      <div class="webhook__call-body-content">
        <div class="webhook__call-body-label">Request</div>
        <div class="webhook__code-container">
          <pre
            class="webhook__code webhook__code--small"
          ><code>{{ call.request }}</code></pre>
        </div>
      </div>
      <div class="webhook__call-body-content">
        <div class="webhook__call-body-label">Response</div>
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
export default {
  name: 'WebhookCall',
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
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>
