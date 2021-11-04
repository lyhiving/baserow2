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
        <webhook
          :webhook="webhook"
          :table="table"
          @triggerWebhook="triggerWebhook()"
        />
      </div>
    </div>
    <div v-if="!renderList" class="webhook__list">
      <create-webhook-context :table="table" @created="toggleCreate()" />
    </div>
    <trigger-webhook-modal ref="triggerWebhookModal" />
  </Modal>
</template>

<script>
import { mapState } from 'vuex'
import Webhook from './Webhook.vue'
import CreateWebhookContext from './CreateWebhookContext.vue'
import TriggerWebhookModal from './TriggerWebhookModal.vue'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  components: { Webhook, CreateWebhookContext, TriggerWebhookModal },
  mixins: [modal, error],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      renderList: true,
    }
  },
  computed: mapState({
    // arrow functions can make the code very succinct!
    webhooks: (state) => state.webhook.items,
  }),
  methods: {
    triggerWebhook() {
      console.log('trying to run, right?', this.$refs)
      this.$refs.triggerWebhookModal.show()
    },
    toggleCreate() {
      this.renderList = !this.renderList
    },
  },
}
</script>
