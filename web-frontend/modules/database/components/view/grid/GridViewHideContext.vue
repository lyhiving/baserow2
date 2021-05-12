<template>
  <Context ref="context" class="hidings">
    <div>
      <ul class="context__menu">
        <li>
          <button class="button button--primary">
            <i class="fas fa-file-csv"></i>
            Export to CSV
          </button>
        </li>
        <li>
          <button class="button button--primary">
            <i class="fas fa-file-code"></i>
            Export to XML
          </button>
        </li>
      </ul>
    </div>
  </Context>
</template>

<script>
import { mapGetters } from 'vuex'

import context from '@baserow/modules/core/mixins/context'
import { notifyIf } from '@baserow/modules/core/utils/error'
import { clone } from '@baserow/modules/core/utils/object'

export default {
  name: 'ViewHideContext',
  mixins: [context],
  props: {
    fields: {
      type: Array,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      required: true,
    },
    storePrefix: {
      type: String,
      required: true,
    },
  },
  computed: {
    noneSelected() {
      for (const i in this.fields) {
        if (!this.isHidden(this.fields[i].id)) {
          return false
        }
      }
      return true
    },
    allSelected() {
      for (const i in this.fields) {
        if (this.isHidden(this.fields[i].id)) {
          return false
        }
      }
      return true
    },
  },
  beforeCreate() {
    this.$options.computed = {
      ...(this.$options.computed || {}),
      ...mapGetters({
        fieldOptions:
          this.$options.propsData.storePrefix + 'view/grid/getAllFieldOptions',
      }),
    }
  },
  methods: {
    async updateAllFieldOptions(values) {
      const newFieldOptions = {}
      const oldFieldOptions = clone(this.fieldOptions)
      this.fields.forEach((field) => {
        if (!field.primary) {
          newFieldOptions[field.id] = values
        }
      })

      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/grid/updateAllFieldOptions',
          {
            newFieldOptions,
            oldFieldOptions,
          }
        )
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    async updateFieldOptionsOfField(field, values) {
      try {
        await this.$store.dispatch(
          this.storePrefix + 'view/grid/updateFieldOptionsOfField',
          {
            field,
            values,
            oldValues: { hidden: this.fieldOptions[field.id].hidden },
          }
        )
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    isHidden(fieldId) {
      const exists = Object.prototype.hasOwnProperty.call(
        this.fieldOptions,
        fieldId
      )
      return exists ? this.fieldOptions[fieldId].hidden : false
    },
  },
}
</script>
