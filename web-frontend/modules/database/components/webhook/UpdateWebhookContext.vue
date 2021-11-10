<template>
  <div>
    <Error :error="error" />
    <webhook-form
      ref="form"
      :table="table"
      :default-values="webhook"
      @submitted="submit"
      @formchange="handleFormChange"
    >
      <div class="actions">
        <a
          class="button button--primary button--error"
          @click="deleteWebhook()"
        >
          {{ $t('action.delete') }}
        </a>
        <div class="align-right">
          <p v-if="loadedSuccessfully" class="color-success">
            <strong>{{ $t('webhook.successfullyUpdated') }}</strong>
          </p>
          <button
            v-if="!loadedSuccessfully"
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
      loadedSuccessfully: false,
    }
  },
  methods: {
    deleteWebhook() {
      this.$refs.deleteWebhookModal.show()
    },
    handleFormChange() {
      this.loadedSuccessfully = false
    },
    async submit(values) {
      this.loading = true
      const table = this.table
      const webhook = this.webhook
      try {
        await this.$store.dispatch('webhook/update', { table, webhook, values })
        this.loading = false
        this.loadedSuccessfully = true
      } catch (error) {
        this.loading = false
        this.handleError(error)
        this.$refs.form.reset()
      }
    },
  },
}
</script>
