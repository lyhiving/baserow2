<template>
  <Modal>
    <h2 class="box__title">Webhooks {{ table.name }} table</h2>
    <Error :error="error"></Error>
    <div class="actions">
      <div class="align-right">
        <button class="button button--large button--primary">
          Create Webhook
          <i class="fas fa-plus"></i>
        </button>
      </div>
    </div>
    <div class="webhook-accordion__list">
      <div v-for="webhook in webhooks" :key="webhook.id">
        <webhook-accordion :webhook="webhook" :table="table" />
      </div>
    </div>
  </Modal>
</template>

<script>
import { mapState } from 'vuex'
import WebhookAccordion from './WebhookAccordion.vue'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  components: { WebhookAccordion },
  mixins: [modal, error],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  computed: mapState({
    // arrow functions can make the code very succinct!
    webhooks: (state) => state.webhook.items,
  }),
  methods: {},
}
</script>
