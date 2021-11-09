<template>
  <div>
    <Error :error="error" />
    <webhook-form
      ref="form"
      :table="table"
      :default-values="webhook"
      @submitted="submit"
    >
      <div class="actions">
        <button
          class="button button--primary button--error"
          @click="deleteWebhook()"
        >
          {{ $t('action.delete') }}
        </button>
        <div class="align-right">
          <button
            class="button button--primary"
            :class="{ 'button--loading': loading }"
            :disabled="loading"
          >
            {{ $t('action.save') }}
          </button>
        </div>
      </div>
      <delete-webhook-modal
        ref="deleteWebhookModal"
        :webhook="webhook"
        :table="table"
      />
    </webhook-form>
  </div>
</template>

<script>
import WebhookForm from '@baserow/modules/database/components/webhook/WebhookForm'
import DeleteWebhookModal from '@baserow/modules/database/components/webhook/DeleteWebhookModal.vue'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'UpdateWebhookContext',
  components: { WebhookForm, DeleteWebhookModal },
  mixins: [error],
  props: {
    table: {
      type: Object,
      required: true,
    },
    webhook: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
    }
  },
  methods: {
    deleteWebhook() {
      this.$refs.deleteWebhookModal.show()
    },
    async submit(values) {
      this.loading = true
      const table = this.table
      const webhook = this.webhook
      try {
        await this.$store.dispatch('webhook/update', { table, webhook, values })
        this.loading = false
      } catch (error) {
        this.loading = false
        this.handleError(error)
        this.$refs.form.reset()
      }
    },
  },
}
</script>
