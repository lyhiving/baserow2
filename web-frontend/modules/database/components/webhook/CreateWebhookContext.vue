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
      const table = this.table
      try {
        await this.$store.dispatch('webhook/create', { table, values })
        this.$emit('created')
      } catch {
        console.log('LEIDER NICHT')
      }
    },
  },
}
</script>
