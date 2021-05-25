<template>
  <div>
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">Encoding</label>
          <div class="control__elements">
            <CharsetDropdown
              v-model="localValue.exportCharset"
              :disabled="loading"
            >
            </CharsetDropdown>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CharsetDropdown from '@baserow/modules/core/components/helpers/CharsetDropdown'

export default {
  name: 'TableXMLExporter',
  components: { CharsetDropdown },
  props: {
    value: {
      type: Object,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      localValue: {
        exportCharset: 'utf-8',
      },
    }
  },
  watch: {
    localValue: {
      handler(newVal) {
        this.$emit('input', newVal)
      },
      deep: true,
    },
  },
  created() {
    this.$emit('input', this.localValue)
  },
}
</script>
