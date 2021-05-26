<template>
  <Modal>
    <h2 class="box__title">Export {{ table.name }}</h2>
    <ExportTableForm :table="table" :view="view"></ExportTableForm>
  </Modal>
</template>

<script>
import modal from '@baserow/modules/core/mixins/modal'
import ExportTableForm from '@baserow/modules/database/components/export/ExportTableForm'

export default {
  name: 'ExportTableModal',
  components: { ExportTableForm },
  mixins: [modal],
  props: {
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: false,
      default: null,
    },
  },
}
</script>
