<template>
  <div>
    <div @click="toggleExpand">
      <slot :isExpanded="isExpanded" name="header"></slot>
    </div>
    <div
      :class="{
        'accordion--expanded': isExpanded,
        'accordion--closed': !isExpanded,
      }"
    >
      <slot name="body"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Accordion',
  data() {
    return {
      isExpanded: false,
    }
  },
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>
