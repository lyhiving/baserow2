<template>
  <webhook-form
    ref="form"
    :table="table"
    :default-values="webhook"
    @submitted="submit"
  >
    <div class="actions">
      <button
        class="button button--primary button--error"
        :class="{ 'button--loading': loading }"
        :disabled="loading"
        @click="deleteWebhook()"
      >
        Delete
      </button>
      <div class="align-right">
        <a
          href="#"
          class="button button--ghost"
          @click="$emit('triggerWebhook')"
          >Trigger test webhook</a
        >
        <button
          class="button button--primary"
          :class="{ 'button--loading': loading }"
          :disabled="loading"
        >
          Save
        </button>
      </div>
    </div>
    <delete-webhook-modal
      ref="deleteWebhookModal"
      :webhook="webhook"
      :table="table"
    />
  </webhook-form>
</template>

<script>
import WebhookForm from '@baserow/modules/database/components/webhook/WebhookForm'
import DeleteWebhookModal from './DeleteWebhookModal.vue'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'UpdateWebhookContext',
  components: { WebhookForm, DeleteWebhookModal },
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
  watch: {
    webhook() {
      // If the field values are updated via an outside source, think of real time
      // collaboration or via the modal, we want to reset the form so that it contains
      // the correct base values.
      this.$nextTick(() => {
        this.$refs.form.reset()
      })
    },
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
        notifyIf(error, 'webhook')
      }
    },
  },
}
</script>
