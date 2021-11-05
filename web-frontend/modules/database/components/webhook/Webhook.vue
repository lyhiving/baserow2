<template>
  <div>
    <div class="webhook" :class="{ 'webhook--open': isExpanded }">
      <div class="webhook__head">
        <div class="webhook__head-left">
          <div class="webhook__head-name">
            {{ webhook.name }}
          </div>
          <div class="webhook__head-details">
            <div class="webhook__head-details-target">
              {{ webhook.url }}
            </div>
            <a href="#" class="webhook__head-toggle" @click="toggleExpand()">
              details
              <i
                class="fas webhook__head-toggle-icon"
                :class="{
                  'fa-chevron-down': !isExpanded,
                  'fa-chevron-up': isExpanded,
                }"
              ></i>
            </a>
          </div>
        </div>
        <div class="webhook__head-right">
          <div class="webhook__head-trigger">
            {{ webhookTriggerDescription }}
          </div>
          <div class="webhook__head-call">
            <div class="webhook__head-date">
              {{ `Last call: ${lastCall}` }}
            </div>
            <span class="webhook__head-call-state" :class="lastStatusClass">{{
              lastStatus
            }}</span>
          </div>
        </div>
      </div>
      <div class="webhook__body">
        <Tabs>
          <Tab title="Edit">
            <update-webhook-context
              :webhook="webhook"
              :table="table"
              @triggerWebhook="$emit('triggerWebhook')"
            />
          </Tab>
          <Tab title="Call log">
            <div v-for="call in webhook.calls" :key="call.id">
              <webhook-call :call="call" />
            </div>
          </Tab>
        </Tabs>
      </div>
    </div>
  </div>
</template>

<script>
import moment from '@baserow/modules/core/moment'
import Tabs from '@baserow/modules/core/components/Tabs.vue'
import Tab from '@baserow/modules/core/components/Tab.vue'
import UpdateWebhookContext from './UpdateWebhookContext.vue'
import WebhookCall from './WebhookCall.vue'

export default {
  name: 'Webhook',
  components: { Tabs, Tab, UpdateWebhookContext, WebhookCall },
  props: {
    webhook: {
      type: Object,
      required: true,
    },
    table: {
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
      const calls = this.$props.webhook.calls
      if (calls.length > 0) {
        return moment(calls[0].called_time).format('YYYY-MM-DD HH:mm:ss')
      } else {
        return 'Not called yet'
      }
    },
    lastStatus() {
      const calls = this.$props.webhook.calls
      if (calls.length > 0) {
        return calls[0].status_code
      } else {
        return 'No status'
      }
    },
    lastStatusClass() {
      const calls = this.$props.webhook.calls
      if (calls.length > 0) {
        if (calls[0].status_code >= 200 && calls[0].status_code <= 299) {
          return 'webhook__head-call-state--ok'
        } else {
          return 'webhook__head-call-state--error'
        }
      } else {
        return ''
      }
    },
    webhookTriggerDescription() {
      if (this.$props.webhook.include_all_events) {
        return 'Sends on every event'
      } else {
        const numberOfEvents = this.$props.webhook.events.length
        return `Sends on ${numberOfEvents} ${
          numberOfEvents <= 1 ? 'event' : 'events'
        }`
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
