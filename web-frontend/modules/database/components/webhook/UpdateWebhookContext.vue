<template>
  <webhook-form
    ref="form"
    :table="table"
    :default-values="webhook"
    @submitted="submit"
  >
    <div class="context__form-actions">
      <button
        class="button"
        :class="{ 'button--loading': loading }"
        :disabled="loading"
      >
        {{ $t('action.change') }}
      </button>
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
      const table = this.table
      const webhook = this.webhook
      console.log('IST WEBHOOK HIER?: ', webhook)
      try {
        await this.$store.dispatch('webhook/update', { table, webhook, values })
      } catch {
        console.log('LEIDER NICHT')
      }
    },
    async submit_old(values) {
      this.loading = true

      const type = values.type
      delete values.type

      try {
        const forceUpdateCallback = await this.$store.dispatch('field/update', {
          field: this.field,
          type,
          values,
          forceUpdate: false,
        })
        // The callback must be called as soon the parent page has refreshed the rows.
        // This is to prevent incompatible values when the field changes before the
        // actual column row has been updated. If there is nothing to refresh then the
        // callback must still be called.
        const callback = async () => {
          await forceUpdateCallback()
          this.$refs.form.reset()
          this.loading = false
          this.hide()
          this.$emit('updated')
        }
        this.$emit('update', { callback })
      } catch (error) {
        this.loading = false
        const handledByForm = this.$refs.form.handleErrorByForm(error)
        if (!handledByForm) {
          notifyIf(error, 'field')
        }
      }
    },
  },
}
</script>
