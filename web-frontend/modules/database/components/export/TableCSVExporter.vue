<template>
  <div>
    <div class="row">
      <div class="col col-4">
        <div class="control">
          <label class="control__label">Column separator</label>
          <div class="control__elements">
            <Dropdown
              v-model="localValue.csvColumnSeparator"
              :disabled="loading"
            >
              <DropdownItem name="," value="comma"></DropdownItem>
              <DropdownItem name=";" value="semi"></DropdownItem>
              <DropdownItem name="|" value="pipe"></DropdownItem>
              <DropdownItem name="<tab>" value="tab"></DropdownItem>
              <DropdownItem
                name="record separator (30)"
                value="record_separator"
              ></DropdownItem>
              <DropdownItem
                name="unit separator (31)"
                value="unit_separator"
              ></DropdownItem>
            </Dropdown>
          </div>
        </div>
      </div>
      <div class="col col-8">
        <div class="control">
          <label class="control__label">Encoding</label>
          <div class="control__elements">
            <CharsetDropdown
              v-model="localValue.csvEncoding"
              :disabled="loading"
            >
            </CharsetDropdown>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-6">
        <div class="control">
          <label class="control__label">First row is header</label>
          <div class="control__elements">
            <Checkbox v-model="localValue.csvFirstRowHeader" :disabled="loading"
              >yes</Checkbox
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CharsetDropdown from '@baserow/modules/core/components/helpers/CharsetDropdown'
export default {
  name: 'TableCSVExporter',
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
        csvFirstRowHeader: true,
        csvEncoding: 'utf-8',
        csvColumnSeparator: 'comma',
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
