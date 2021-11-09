<template>
  <div>
    <Error :error="error" />
    <webhook-form ref="form" :table="table" :create="true" @submitted="submit">
      <div class="actions">
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
    </webhook-form>
  </div>
</template>

<script>
import WebhookForm from '@baserow/modules/database/components/webhook/WebhookForm'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'CreateWebhookContext',
  components: { WebhookForm },
  mixins: [error],
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
        this.handleError(error)
      }
    },
  },
}
</script>
