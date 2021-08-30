<template>
  <textarea
    ref="textarea"
    rows="1"
    v-bind="$attrs"
    v-on="$listeners"
    @input="resize()"
  ></textarea>
</template>
<script>
export default {
  name: 'AutoResizingTextarea',
  mounted() {
    this.resize()
  },
  methods: {
    resize() {
      const $textarea = this.$refs.textarea
      $textarea.style.height = $textarea.scrollHeight + 'px'
    },
  },
}
</script>
