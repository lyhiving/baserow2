/**
 * Helper mixin for webhooks.
 */
export default {
  methods: {
    statusDescription(statusCode) {
      if (!statusCode) {
        return this.$t('webhook.status.noStatus')
      }
      if (statusCode >= 200 && statusCode <= 299) {
        return `${statusCode} ${this.$t('webhook.status.statusOK')}`
      } else {
        return `${statusCode} ${this.$t('webhook.status.statusNotOK')}`
      }
    },
  },
}
