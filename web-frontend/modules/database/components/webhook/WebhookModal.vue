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
    <webhook-list
      :table="table"
      :render-list="renderList"
      @triggerWebhook="triggerWebhook()"
    />
    <div v-if="!renderList" class="webhook__list">
      <create-webhook-context :table="table" @created="toggleCreate()" />
    </div>
    <trigger-webhook-modal ref="triggerWebhookModal" />
  </Modal>
</template>

<script>
import WebhookList from './WebhookList.vue'
import CreateWebhookContext from './CreateWebhookContext.vue'
import TriggerWebhookModal from './TriggerWebhookModal.vue'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  components: {
    CreateWebhookContext,
    TriggerWebhookModal,
    WebhookList,
  },
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
