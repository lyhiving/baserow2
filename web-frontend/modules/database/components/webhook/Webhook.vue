<template>
  <div>
    <div class="webhook" :class="{ 'webhook--open': isExpanded }">
      <div class="webhook__head">
        <div class="webhook__head-left">
          <div class="webhook__head-name">
            {{
              !webhook.active ? `${webhook.name} - Deactivated` : webhook.name
            }}
          </div>
          <div class="webhook__head-details">
            <div class="webhook__head-details-target">
              {{ webhook.url }}
            </div>
            <a href="#" class="webhook__head-toggle" @click="toggleExpand()">
              {{ $t('webhook.details') }}
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
            {{
              $tc('webhook.triggerDescription', calculateNumberOfEvents, {
                count: calculateNumberOfEvents,
              })
            }}
          </div>
          <div class="webhook__head-call">
            <div class="webhook__head-date">
              {{ $t('webhook.lastCall', { lastCallTime: lastCall }) }}
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
            <update-webhook-context :webhook="webhook" :table="table" />
          </Tab>
          <Tab title="Call log">
            <p v-if="webhook.calls.length <= 0">{{ $t('webhook.noCalls') }}</p>
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
import webhook from '@baserow/modules/database/mixins/webhook'

export default {
  name: 'Webhook',
  components: { Tabs, Tab, UpdateWebhookContext, WebhookCall },
  mixins: [webhook],
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
        return this.$t('webhook.noCalls')
      }
    },
    lastStatus() {
      const calls = this.$props.webhook.calls
      if (calls.length > 0) {
        return this.statusDescription(calls.status_code)
      } else {
        return ''
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
    calculateNumberOfEvents() {
      if (this.$props.webhook.include_all_events) {
        return 0
      } else {
        return this.$props.webhook.events.length
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

<i18n>
{
  "en": {
    "webhook": {
      "details": "details",
      "lastCall": "Last call: {lastCallTime}",
      "noCalls": "Not called yet.",
      "triggerDescription": "Sends on every event | Sends on {count} event | Send on {count} events"
    }
  },
  "fr": {
    "webhook": {
      "details": "@TODO",
      "lastCall": "@TODO",
      "noCalls": "@TODO",
      "triggerDescription": "@TODO"
    }
  }
}
</i18n>
