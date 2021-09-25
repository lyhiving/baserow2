<template>
  <textarea
    ref="textarea"
    v-model="innerValue"
    rows="1"
    @blur="$emit('blur', $event)"
    @click="$emit('click', $event)"
    @keyup="$emit('keyup', $event)"
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
  },
}
</script>
