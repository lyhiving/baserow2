<template>
  <webhook-form
    ref="form"
    :table="table"
    :default-values="webhook"
    :create="true"
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
  name: 'CreateWebhookContext',
  components: { WebhookForm },
  props: {
    table: {
      type: Object,
      required: true,
    },
    webhook: {
      type: Object,
      required: false,
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
      try {
        await this.$store.dispatch('webhook/create', { table, values })
        this.loading = false
        this.$emit('created')
      } catch (error) {
        this.loading = false
        notifyIf(error, 'webhook')
      }
    },
  },
}
</script>
