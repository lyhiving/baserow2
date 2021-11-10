<template>
  <div v-if="renderList" class="webhook__list">
    <p v-if="webhooks.length === 0" class="margin-top-2">
      {{ $t('webhookList.noWebhooksMessage') }}
    </p>
    <div v-for="webhook in webhooks" :key="webhook.id">
      <webhook :webhook="webhook" :table="table" />
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import Webhook from './Webhook.vue'

export default {
  name: 'WebhookList',
  components: {
    Webhook,
  },
  props: {
    table: {
      type: Object,
      required: true,
    },
    renderList: {
      type: Boolean,
      required: true,
    },
  },
  computed: mapState({
    webhooks: (state) => state.webhook.items,
  }),
  async created() {
    await this.$store.dispatch('webhook/fetchAll', this.$props.table, {
      root: true,
    })
  },
}
</script>

<i18n>
{
  "en": {
    "webhookList": {
      "noWebhooksMessage": "You have not created any webhooks yet. Webhooks can be used in order to inform 3rd party systems about a row in Baserow being created, updated or deleted."
    }
  },
  "fr": {
    "webhookList": {
      "noWebhooksMessage": "@TODO"
    }
  }
}
</i18n>
