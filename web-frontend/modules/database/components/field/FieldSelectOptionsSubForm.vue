<template>
  <div>
    <div class="control">
      <label class="control__label control__label--small">{{
        $t('fieldSingleSelectSubForm.optionsLabel')
      }}</label>
      <div class="control__elements">
        <FieldSelectOptions
          ref="selectOptions"
          v-model="values.select_options"
        ></FieldSelectOptions>
      </div>
    </div>
  </div>
</template>

<script>
import form from '@baserow/modules/core/mixins/form'
import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import FieldSelectOptions from '@baserow/modules/database/components/field/FieldSelectOptions'

export default {
  name: 'FieldSelectOptionsSubForm',
  components: { FieldSelectOptions },
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['select_options'],
      values: {
        select_options: [],
      },
    }
  },
  methods: {
    isFormValid() {
      this.$refs.selectOptions.$v.$touch()
      return !this.$refs.selectOptions.$v.$invalid
    },
    getFormValues() {
      // We only want to send the select option item with an ID to the backend
      // if that ID was created by the backend. Every ID lower than 0 was created
      // locally by the FieldSelectOptions component, hence we want to remove this
      // ID before making the API request.
      const newSelectOptions = this.values.select_options.map((item) => {
        if (item.id < 0) {
          delete item.id
        }
        return item
      })
      return { select_options: newSelectOptions }
    },
  },
}
</script>

<i18n>
{
  "en": {
    "fieldSingleSelectSubForm": {
      "optionsLabel": "Options"
    }
  },
  "fr": {
    "fieldSingleSelectSubForm": {
      "optionsLabel": "Options"
    }
  }
}
</i18n>
