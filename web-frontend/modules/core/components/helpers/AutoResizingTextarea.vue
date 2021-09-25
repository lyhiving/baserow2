<template>
  <textarea
    ref="textarea"
    v-model="innerValue"
    rows="1"
    @blur="$emit('blur', $event)"
    @click="$emit('click', $event)"
    @keyup="handleKeyUp"
    @keydown="handleKeyDown"
    @input="resize()"
  ></textarea>
</template>
<script>
export default {
  name: 'AutoResizingTextarea',
  props: {
    value: {
      required: true,
      type: String,
    },
  },
  computed: {
    innerValue: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
  },
  mounted() {
    this.resize()
  },
  methods: {
    focus() {},
    resize() {
      const $textarea = this.$refs.textarea
      $textarea.style.height = $textarea.scrollHeight + 'px'
    },
    handleKeyUp(event) {
      if (event.keyCode === 9) {
        event.preventDefault()
      } else {
        this.$emit('keyup', event)
      }
    },
    handleKeyDown(event) {
      if (event.keyCode === 9) {
        event.preventDefault()
        this.$emit('tab')
      } else {
        this.$emit('keydown', event)
      }
    },
  },
}
</script>
