<template>
  <div>
    <div class="control">
      <div
        v-if="linkRowFieldsInThisTable.length === 0"
        class="alert alert--error context__alert"
      >
        <p class="alert__content">
          {{ $t('fieldLookupSubForm.noTable') }}
        </p>
      </div>
      <div v-if="linkRowFieldsInThisTable.length > 0">
        <label class="control__label control__label--small">
          {{ $t('fieldLookupSubForm.selectThroughFieldLabel') }}
        </label>
        <div class="control__elements">
          <div class="control">
            <Dropdown
              v-model="values.through_field"
              :class="{ 'dropdown--error': $v.values.through_field.$error }"
              @hide="$v.values.through_field.$touch()"
              @input="throughFieldSelected"
            >
              <DropdownItem
                v-for="field in linkRowFieldsInThisTable"
                :key="field.id"
                :name="field.name"
                :value="field.id"
              ></DropdownItem>
            </Dropdown>
            <div v-if="$v.values.through_field.$error" class="error">
              {{ $t('error.requiredField') }}
            </div>
          </div>
          <div v-if="loading" class="loading-absolute-center"></div>
          <div v-else-if="values.through_field" class="control">
            <label class="control__label control__label--small">
              {{ $t('fieldLookupSubForm.selectTargetFieldLabel') }}
            </label>
            <Dropdown
              v-model="values.target_field"
              :class="{ 'dropdown--error': $v.values.target_field.$error }"
              @hide="$v.values.target_field.$touch()"
            >
              <DropdownItem
                v-for="field in fieldsInThroughTable"
                :key="field.id"
                :name="field.name"
                :value="field.id"
              ></DropdownItem>
            </Dropdown>
            <div
              v-if="values.through_field && $v.values.target_field.$error"
              class="error"
            >
              {{ $t('error.requiredField') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { required } from 'vuelidate/lib/validators'

import form from '@baserow/modules/core/mixins/form'
import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import { notifyIf } from '@baserow/modules/core/utils/error'
import FieldService from '@/modules/database/services/field'

export default {
  name: 'FieldLookupSubForm',
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['through_field', 'target_field'],
      values: {
        through_field: null,
        target_field: null,
      },
      loading: false,
      fieldsInThroughTable: [],
    }
  },
  computed: {
    linkRowFieldsInThisTable() {
      const fields = this.$store.getters['field/getAll']
      return fields.filter((f) => f.type === 'link_row')
    },
  },
  watch: {
    'values.through_field'() {
      this.throughFieldSelected()
    },
  },
  validations: {
    values: {
      through_field: { required },
      target_field: { required },
    },
  },
  methods: {
    async throughFieldSelected() {
      if (!this.values.through_field) {
        return
      }
      this.loading = true

      try {
        const selectedField = this.$store.getters['field/get'](
          this.values.through_field
        )
        if (selectedField && selectedField.link_row_table) {
          const { data } = await FieldService(this.$client).fetchAll(
            selectedField.link_row_table
          )
          this.fieldsInThroughTable = data
        }
      } catch (error) {
        notifyIf(error, 'view')
      }

      this.loading = false
    },
    isValid() {
      return (
        form.methods.isValid().call(this) &&
        this.linkRowFieldsInThisTable.length > 0
      )
    },
  },
}
</script>

<i18n>
{
  "en": {
    "fieldLookupSubForm": {
      "noTable": "You need at least one link row field to create a lookup field.",
      "selectThroughFieldLabel": "Select a link row field",
      "selectTargetFieldLabel": "Select a field to lookup"
    }
  },
  "fr": {
    "fieldLookupSubForm": {
      "noTable": "Vous devez créer au moins une autre table dans la même base de données pour pouvoir créer un lien.",
      "selectThroughFieldLabel": "#TODO",
      "selectTargetFieldLabel": "#TODO"
    }
  }
}
</i18n>
