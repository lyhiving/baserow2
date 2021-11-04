<template>
  <component
    :is="getComponent(field)"
    v-if="getComponent(field)"
    :field="field"
    :value="value"
    class="active"
  ></component>
  <div v-else class="grid-view__cell cell-error active">Unknown Field Type</div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
  methods: {
    getComponent(field) {
      const formulaType = this.$registry.get('formula_type', field.formula_type)
      return formulaType.getFunctionalGridViewFieldComponent()
    },
  },
}
</script>
