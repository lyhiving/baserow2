<template>
  <Modal>
    <h2 class="box__title">Webhooks {{ table.name }} table</h2>
    <Error :error="error"></Error>
    <div class="actions">
      <div class="align-right">
        <a href="#" class="button" @click="toggleCreate()">
          {{ renderList ? 'Create web hook' : 'Back to list' }}
          <i class="fas fa-plus"></i>
        </a>
      </div>
    </div>
    <div v-if="renderList" class="webhook__list">
      <div v-for="webhook in webhooks" :key="webhook.id">
        <webhook-accordion :webhook="webhook" :table="table" />
      </div>
    </div>
    <div v-if="!renderList" class="webhook__list">
      <create-webhook-context :table="table" @created="toggleCreate()" />
    </div>
  </Modal>
</template>

<script>
import { mapState } from 'vuex'
import WebhookAccordion from './WebhookAccordion.vue'
import CreateWebhookContext from './CreateWebhookContext.vue'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  components: { WebhookAccordion, CreateWebhookContext },
  mixins: [modal, error],
  data() {
    return {
      renderList: true,
    }
  },
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
  methods: {
    toggleCreate() {
      this.renderList = !this.renderList
    },
  },
}
</script>
