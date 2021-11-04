<template>
  <Modal>
    <h2 class="box__title">Delete {{ webhook.name }}</h2>
    <Error :error="error"></Error>
    <div>
      <p>
        Are you sure you want to delete the webhook
        <strong>{{ webhook.name }}</strong
        >? You will not be able to restore it later.
      </p>
      <div class="actions">
        <div class="align-right">
          <button
            class="button button--large button--error"
            :class="{ 'button--loading': loading }"
            :disabled="loading"
            @click="deleteWebhook()"
          >
            Delete webhook
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script>
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'DeleteViewModal',
  mixins: [modal, error],
  props: {
    webhook: {
      type: Object,
      required: true,
    },
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
    async deleteWebhook() {
      this.loading = true
      const table = this.table
      const webhook = this.webhook
      try {
        await this.$store.dispatch('webhook/delete', { table, webhook })
        this.loading = false
      } catch (error) {
        this.loading = false
        notifyIf(error, 'webhook')
      }
    },
  },
}
</script>
