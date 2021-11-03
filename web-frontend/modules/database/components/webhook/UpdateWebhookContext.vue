<template>
  <webhook-form
    ref="form"
    :table="table"
    :default-values="webhook"
    @submitted="submit"
  >
    <div class="actions">
      <a href="#" class="button button--ghost">Trigger test webhook</a>
      <div class="align-right">
        <button
          class="button button--primary"
          :class="{ 'button--loading': loading }"
          :disabled="loading"
        >
          Save
        </button>
      </div>
    </div>
  </webhook-form>
</template>

<script>
import WebhookForm from '@baserow/modules/database/components/webhook/WebhookForm'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'UpdateWebhookContext',
  components: { WebhookForm },
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
    field() {
      // If the field values are updated via an outside source, think of real time
      // collaboration or via the modal, we want to reset the form so that it contains
      // the correct base values.
      this.$nextTick(() => {
        this.$refs.form.reset()
      })
    },
  },
  methods: {
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
