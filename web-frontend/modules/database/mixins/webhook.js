/**
 * Helper mixin for webhooks.
 */
export default {
  methods: {
    statusDescription(statusCode) {
      if (!statusCode) {
        return 'NO STATUS'
      }
      if (statusCode >= 200 || statusCode <= 299) {
        return `${statusCode} OK`
      } else {
        return `${statusCode} NOT OK`
      }
    },
  },
}
