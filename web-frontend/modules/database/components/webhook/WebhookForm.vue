<template>
  <form @submit.prevent="submit">
    <div class="row">
      <div class="col col-12">
        <div class="control">
          <label class="control__label">Name</label>
          <div class="control__elements">
            <input
              v-model="values.name"
              class="input"
              :class="{ 'input--error': $v.values.name.$error }"
            />
            <div v-if="$v.values.name.$error" class="error">
              This field is required.
            </div>
          </div>
        </div>
      </div>
      <div v-if="!create" class="col col-4">
        <div class="control">
          <label class="control__label">Status</label>
          <div class="control__elements">
            <Checkbox v-model="values.active">Active</Checkbox>
          </div>
        </div>
      </div>
      <div class="col" :class="{ 'col-6': !create, 'col-12': create }">
        <div class="control">
          <label class="control__label">User field names</label>
          <div class="control__elements">
            <Checkbox v-model="values.use_user_field_names">{{
              values.use_user_field_names
                ? 'Send user field names'
                : 'Send field ids'
            }}</Checkbox>
          </div>
        </div>
      </div>
      <div class="col col-4">
        <div class="control">
          <div class="control__label">Method</div>
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
            <input
              v-model="values.url"
              class="input"
              :class="{ 'input--error': $v.values.url.$error }"
            />
            <div v-if="$v.values.url.$error" class="error">
              This field is required and needs to be a valid url.
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="control">
      <label class="control__label"
        >Which events should trigger this webhook?</label
      >
      <div class="control__elements">
        <Radio v-model="radio" value="all" @input="triggerAllEvents"
          >Send me everything</Radio
        >
        <Radio v-model="radio" value="custom" @input="selectSingleEvent">
          Let me select individual events
        </Radio>
        <div v-if="radio === 'custom'" class="webhook__types">
          <Checkbox v-model="events.rowCreated" class="webhook__type"
            >When a row is created</Checkbox
          >
          <Checkbox v-model="events.rowUpdated" class="webhook__type"
            >When a row is updated</Checkbox
          >
          <Checkbox v-model="events.rowDeleted" class="webhook__type"
            >When a row is deleted</Checkbox
          >
        </div>
      </div>
    </div>
    <div class="control">
      <div class="control__label">Additional headers</div>
      <div class="control__elements">
        <div
          v-for="(input, index) in defaultHeaders"
          :key="`headerInput-${index}`"
          class="webhook__header"
        >
          <div class="webhook__header-row">
            <input
              v-model="input.header"
              class="input webhook__header-key"
              :disabled="true"
            />
            <input
              v-model="input.value"
              class="input webhook__header-value"
              :disabled="true"
            />
          </div>
        </div>
        <div v-if="values.headers.length === 0">
          <a href="#" class="button button--ghost" @click="addHeaderField()"
            >Add additional headers</a
          >
        </div>
        <div v-if="values.headers.length > 0">
          <div
            v-for="(input, index) in values.headers"
            :key="`headerInput-${index}`"
            class="webhook__header"
          >
            <div class="webhook__header-row">
              <input
                v-model="input.header"
                class="input webhook__header-key"
                placeholder="Header"
              />
              <input
                v-model="input.value"
                class="input webhook__header-value"
                placeholder="Value"
                @input="inputChange(index, input)"
              />
              <a
                v-if="!lastHeaderElement(index)"
                href="#"
                class="button button--error webhook__header-delete"
                @click="removeHeaderField(index)"
              >
                <i class="fas fa-trash button__icon"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="control">
      <webhook-example :userFieldNames="values.use_user_field_names" />
    </div>
    <slot></slot>
  </form>
</template>

<script>
import { required } from 'vuelidate/lib/validators'

import form from '@baserow/modules/core/mixins/form'
import Checkbox from '@baserow/modules/core/components/Checkbox.vue'
import Radio from '@baserow/modules/core/components/Radio.vue'
import WebhookExample from './WebhookExample.vue'

export default {
  name: 'WebhookForm',
  components: {
    Checkbox,
    Radio,
    WebhookExample,
  },
  mixins: [form],
  props: {
    table: {
      type: Object,
      required: true,
    },
    create: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      allowedValues: [
        'name',
        'url',
        'request_method',
        'include_all_events',
        'use_user_field_names',
        'headers',
        'events',
        'active',
      ],
      values: {
        name: '',
        active: true,
        use_user_field_names: true,
        url: '',
        request_method: 'POST',
        headers: [{ header: '', value: '' }],
      },
      defaultHeaders: [{ header: 'Content-type', value: 'application/json' }],
      radio: 'all',
      events: {
        rowCreated: false,
        rowUpdated: false,
        rowDeleted: false,
      },
      eventsMapping: {
        rowCreated: 'row.created',
        rowUpdated: 'row.updated',
        rowDeleted: 'row.deleted',
      },
    }
  },
  created() {
    if (!this.$props.create) {
      if (this.defaultValues.include_all_events) {
        this.radio = 'all'
      } else {
        this.radio = 'custom'
        this.defaultValues.events.forEach((event) => {
          for (const [key, value] of Object.entries(this.eventsMapping)) {
            if (value === event.event_type) {
              this.events[key] = true
            }
          }
        })
      }
    }
  },
  validations: {
    values: {
      name: { required },
      url: { required },
    },
  },
  methods: {
    inputChange(index, input) {
      if (this.lastHeaderElement(index) && input.header !== '') {
        this.addHeaderField()
      }
    },
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
    createEventsList() {
      const list = []
      for (const [key, value] of Object.entries(this.events)) {
        if (value) {
          list.push(this.eventsMapping[key])
        }
      }
      return list
    },
    getHeaderValues() {
      // remove empty headers and values
      const result = this.values.headers.filter((item) => {
        const bothNotEmpty = item.header !== '' && item.values !== ''
        const headerNotEmpty = item.header !== ''
        return bothNotEmpty || headerNotEmpty
      })
      return result
    },
    getFormValues() {
      const headers = this.getHeaderValues()
      if (this.radio === 'custom') {
        const events = this.createEventsList()
        return { ...this.values, include_all_events: false, events, headers }
      } else {
        return { ...this.values, include_all_events: true, headers }
      }
    },
  },
}
</script>
