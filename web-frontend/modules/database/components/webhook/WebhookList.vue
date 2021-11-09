<template>
  <div v-if="renderList" class="webhook__list">
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

<style></style>
