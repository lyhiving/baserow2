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
            {{ webhook.name }}
          </div>
          <div class="webhook__head-call">
            <div class="webhook__head-date">Last call: 2021-01-01 12:00</div>
            <span class="webhook__head-call-state webhook__head-call-state--ok"
              >200 OK</span
            >
          </div>
        </div>
      </div>
      <div class="webhook__body">
        <Tabs>
          <Tab title="Edit">
            <update-webhook-context :webhook="webhook" :table="table" />
          </Tab>
          <Tab title="Call log">
            <div v-for="call in webhookCalls" :key="call.id">
              <webhook-call :call="call" />
            </div>
          </Tab>
        </Tabs>
      </div>
    </div>
  </div>
</template>

<script>
import Tabs from '@baserow/modules/core/components/Tabs.vue'
import Tab from '@baserow/modules/core/components/Tab.vue'
import UpdateWebhookContext from './UpdateWebhookContext.vue'
import WebhookCall from './WebhookCall.vue'
import WebhookService from '@baserow/modules/database/services/webhook'

export default {
  name: 'WebhookAccordion',
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
      webhookCalls: [],
    }
  },
  async created() {
    const data = await WebhookService(this.$client).fetchAllCalls(
      this.$props.table.id,
      this.$props.webhook.id
    )
    this.webhookCalls = data.data
  },
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>
