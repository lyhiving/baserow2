<template>
  <webhook-form ref="form" :table="table" :create="true" @submitted="submit">
    <div class="actions">
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
  },
  data() {
    return {
      loading: false,
    }
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
