<template>
  <div>
    <div class="select-options">
      <div
        v-for="(item, index) in value"
        :key="item.id"
        v-sortable="{
          id: item.id,
          update: order,
          handle: '[data-sortable-handle]',
          marginTop: -3,
        }"
        class="select-options__item"
      >
        <div class="select-options__drag-handle" data-sortable-handle></div>
        <a
          :ref="'color-select-' + index"
          :class="'select-options__color' + ' background-color--' + item.color"
          @click="openColor(index)"
        >
          <i class="fas fa-caret-down"></i>
        </a>
        <input
          v-model="item.value"
          class="input select-options__value"
          :class="{ 'input--error': $v.value.$each[index].value.$error }"
          @input="$emit('input', value)"
          @blur="$v.value.$each[index].value.$touch()"
        />
        <a class="select-options__remove" @click.stop.prevent="remove(index)">
          <i class="fas fa-times"></i>
        </a>
      </div>
    </div>
    <a class="add" @click="add()">
      <i class="fas fa-plus add__icon"></i>
      {{ $t('fieldSelectOptions.add') }}
    </a>
    <ColorSelectContext
      ref="colorContext"
      @selected="updateColor(colorContextSelected, $event)"
    ></ColorSelectContext>
  </div>
</template>

<script>
import { required } from 'vuelidate/lib/validators'

import ColorSelectContext from '@baserow/modules/core/components/ColorSelectContext'
import { colors } from '@baserow/modules/core/utils/colors'

export default {
  name: 'FieldSelectOptions',
  components: { ColorSelectContext },
  props: {
    value: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      colorContextSelected: -1,
      // When we first add new select options to the field, they don't have an ID yet,
      // which means a user cannot reorder these select options since the reordering
      // depends on the fact that a select option item has an ID. With the
      // localSelectOptionID we create a local ID for the select option simply so that
      // these can be reordered. After creating the field they will get their "real"
      // ID by the backend. It starts at -1 and will decrement for each additional
      // select option added to this field. This is so that the local ID will never
      // interfere with the ID of the select option that it gets in the database.
      localSelectOptionID: -1,
    }
  },
  methods: {
    remove(index) {
      this.$refs.colorContext.hide()
      this.value.splice(index, 1)
      this.$emit('input', this.value)
    },
    add() {
      this.value.push({
        id: this.localSelectOptionID,
        value: '',
        color: colors[Math.floor(Math.random() * colors.length)],
      })
      this.localSelectOptionID--
      this.$emit('input', this.value)
    },
    openColor(index) {
      this.colorContextSelected = index
      this.$refs.colorContext.setActive(this.value[index].color)
      this.$refs.colorContext.toggle(
        this.$refs['color-select-' + index][0],
        'bottom',
        'left',
        4
      )
    },
    updateColor(index, color) {
      this.value[index].color = color
      this.$emit('input', this.value)
    },
    order(newOrder, oldOrder) {
      const sortedValue = this.value
        .slice()
        .sort(
          (a, b) =>
            newOrder.findIndex((id) => id === a.id) -
            newOrder.findIndex((id) => id === b.id)
        )
      this.$emit('input', sortedValue)
    },
  },
  validations: {
    value: {
      $each: {
        value: { required },
      },
    },
  },
}
</script>

<i18n>
{
  "en": {
    "fieldSelectOptions": {
      "add": "Add an option"
    }
  },
  "fr": {
    "fieldSelectOptions": {
      "add": "Ajouter une option"
    }
  }
}
</i18n>
