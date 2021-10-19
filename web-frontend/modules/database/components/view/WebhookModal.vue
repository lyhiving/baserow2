<template>
  <Modal>
    <h2 class="box__title">Webhooks {{ table.name }} table</h2>
    <Error :error="error"></Error>
    <div v-for="webhook in webhooks" :key="webhook.id">
      <p>Blah blah {{ webhook.name }}</p>
    </div>
  </Modal>
</template>

<script>
import { mapState } from 'vuex'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  mixins: [modal, error],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  computed: mapState({
    // arrow functions can make the code very succinct!
    webhooks: (state) => state.webhook.items,
  }),
  methods: {},
}
</script>
