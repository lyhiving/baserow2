<template>
  <accordion>
    <template slot="header" scope="props">
      <div
        class="webhook-accordion"
        :class="{
          'webhook-accordion--open': props.isExpanded,
          'webhook-accordion--deactivated': !webhook.active,
        }"
      >
        <div class="webhook-accordion__header">
          <div class="webhook-accordion__header-column">
            <h4 class="webhook-accordion__header-name">{{ webhook.name }}</h4>
            <div class="webhook-accordion__header-url-row">
              <span class="webhook-accordion__header-url">
                {{ webhook.url }}
              </span>
              <span
                class="webhook-accordion__header-details"
                @click="$emit('click')"
                >details
                <i
                  class="fas"
                  :class="{
                    'fa-angle-up': props.isExpanded,
                    'fa-angle-down': !props.isExpanded,
                  }"
                ></i>
              </span>
            </div>
          </div>
          <div class="webhook-accordion__header-column">
            <div>
              <span class="webhook-accordion__header-trigger-summary">
                Triggers when row is created
              </span>
            </div>
            <div>
              <span class="webhook-accordion__header-last-call">
                Last call: 2021-12-12 14:00
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #body>
      <div class="webhook-accordion__body">
        <tabs>
          <tab title="Edit">
            <update-webhook-context :table="table" :webhook="webhook" />
          </tab>
          <tab title="Call">
            <div>Kann hier was anderes?</div>
          </tab>
        </tabs>
      </div>
    </template>
  </accordion>
</template>

<script>
import Accordion from '@baserow/modules/core/components/Accordion.vue'
import Tabs from '@baserow/modules/core/components/Tabs.vue'
import Tab from '@baserow/modules/core/components/Tab.vue'
import UpdateWebhookContext from '@baserow/modules/database/components/webhook/UpdateWebhookContext.vue'

export default {
  name: 'WebhookAccordion',
  components: { Accordion, Tabs, Tab, UpdateWebhookContext },
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
}
</script>
