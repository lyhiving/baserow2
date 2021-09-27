<template>
  <ul class="formula-field__item-group">
    <li class="formula-field__item-group-title">
      {{ title }}
      {{ getFilterIndicator(unfilteredItems, filteredItems) }}
    </li>
    <li
      v-for="item in filteredItems"
      :key="item.key"
      class="formula-field__item"
      :class="{
        'formula-field__item-selected': item.isSelected,
      }"
    >
      <a
        href="#"
        class="formula-field__item-link"
        @click="$emit('select-item', item)"
      >
        <i class="fas formula-field__item-icon" :class="[item.icon]" />
        {{ item.value }}
      </a>
    </li>
  </ul>
</template>
<script>
export default {
  name: 'FormulaFieldItemGroup',
  props: {
    title: {
      type: String,
      required: true,
    },
    unfilteredItems: {
      type: Array,
      required: true,
    },
    filteredItems: {
      type: Array,
      required: true,
    },
  },
  methods: {
    getFilterIndicator(unfilteredList, filteredList) {
      const numFiltered = unfilteredList.length - filteredList.length
      return numFiltered === 0 ? '' : `(${numFiltered} filtered)`
    },
  },
}
</script>
