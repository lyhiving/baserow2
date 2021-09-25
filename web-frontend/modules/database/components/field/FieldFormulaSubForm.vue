<template>
  <FormulaEditContextMenu :default-values="defaultValues" :table="table">
  </FormulaEditContextMenu>
</template>

<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import FormulaEditContextMenu from '@baserow/modules/database/components/formula/FormulaEditContextMenu'

export default {
  name: 'FieldFormulaSubForm',
  components: {
    FormulaEditContextMenu,
  },
  mixins: [form, fieldSubForm],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      allowedValues: [],
      values: {},
    }
  },
}
</script>
