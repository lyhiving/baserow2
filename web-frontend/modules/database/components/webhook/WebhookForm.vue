<template>
  <form @submit.prevent="submit">
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">Name</label>
          <div class="control__elements">
            <input v-model="values.name" class="input input--large" />
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">Status</label>
          <div class="control__elements">
            <Checkbox v-model="values.active">Active</Checkbox>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-4">
        <div class="control">
          <label class="control__label">Request Method</label>
          <div class="control__elements">
            <Dropdown v-model="values.request_method">
              <DropdownItem name="POST" value="POST"></DropdownItem>
              <DropdownItem name="GET" value="GET"></DropdownItem>
              <DropdownItem name="PATCH" value="PATCH"></DropdownItem>
              <DropdownItem name="PUT" value="PUT"></DropdownItem>
              <DropdownItem name="DELETE" value="DELETE"></DropdownItem>
            </Dropdown>
          </div>
        </div>
      </div>
      <div class="col col-8">
        <div class="control">
          <label class="control__label">URL</label>
          <div class="control__elements">
            <input v-model="values.url" class="input input--large" />
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label"
            >Which events should trigger this webhook?</label
          >
          <div class="control__elements">
            <Checkbox
              v-model="values.include_all_events"
              @input="triggerAllEvents"
              >Send me everything</Checkbox
            >
          </div>
          <div class="control__elements">
            <Checkbox v-model="showIndividualEvents" @input="selectSingleEvent"
              >Let me select individual events</Checkbox
            >
          </div>
        </div>
      </div>
    </div>
    <div v-if="showIndividualEvents" class="row">
      <div class="col col-1"></div>
      <div class="col col-11">
        <div class="control">
          <label class="control__label">Events</label>
          <div class="control__elements">
            <Checkbox v-model="events.rowCreated"
              >When a row is created</Checkbox
            >
            <Checkbox v-model="events.rowUpdated"
              >When a row is updated</Checkbox
            >
            <Checkbox v-model="events.rowDeleted"
              >When a row is deleted</Checkbox
            >
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">Additional Headers</label>
        </div>
      </div>
    </div>
    <div
      v-for="(input, index) in values.headers"
      :key="`headerInput-${index}`"
      class="row"
    >
      <div class="col col-4">
        <div class="control">
          <div class="control__elements">
            <input
              v-model="input.header"
              class="input input--large"
              placeholder="Header"
            />
          </div>
        </div>
      </div>
      <div class="col col-5">
        <div class="control">
          <div class="control__elements">
            <input
              v-model="input.value"
              class="input input--large"
              placeholder="Value"
            />
          </div>
        </div>
      </div>
      <div class="col col-1">
        <div v-if="lastHeaderElement(index)" class="control">
          <div class="control__elements">
            <button
              class="webhook-form__button webhook-form__button--add"
              @click="addHeaderField()"
            >
              <i class="fa fa-plus"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="col col-1">
        <div
          v-if="lastHeaderElement(index) && !firstHeaderElement(index)"
          class="control"
        >
          <div class="control__elements">
            <button
              class="webhook-form__button webhook-form__button--remove"
              @click="removeHeaderField()"
            >
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    <slot></slot>
  </form>
</template>

<script>
import { required } from 'vuelidate/lib/validators'

import form from '@baserow/modules/core/mixins/form'
import Checkbox from '@baserow/modules/core/components/Checkbox.vue'

export default {
  name: 'WebhookForm',
  components: {
    Checkbox,
  },
  mixins: [form],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      allowedValues: [
        'name',
        'url',
        'request_method',
        'include_all_events',
        'headers',
        'events',
        'active',
      ],
      values: {
        name: '',
        active: true,
        url: '',
        request_method: 'POST',
        include_all_events: true,
        headers: [{ header: '', value: '' }],
      },
      showIndividualEvents: false,
      events: {
        rowCreated: false,
        rowUpdated: false,
        rowDeleted: false,
      },
    }
  },
  validations: {
    values: {
      name: { required },
    },
  },
  methods: {
    triggerAllEvents(val) {
      if (val) {
        this.showIndividualEvents = false
        this.resetSelectedEvents()
      }
    },
    selectSingleEvent(val) {
      if (val) {
        this.values.include_all_events = false
      }
    },
    resetSelectedEvents() {
      for (const [key] of Object.entries(this.events)) {
        this.events[key] = false
      }
    },
    addHeaderField() {
      this.values.headers.push({ header: '', value: '' })
    },
    removeHeaderField(index) {
      this.values.headers.splice(index, 1)
    },
    lastHeaderElement(index) {
      return index + 1 === this.values.headers.length
    },
    firstHeaderElement(index) {
      return index === 0
    },
    getFormValues() {
      console.log('JA ICH RENNE MIT GETFORMVALUES')
      return this.values
    },
  },
}
</script>
