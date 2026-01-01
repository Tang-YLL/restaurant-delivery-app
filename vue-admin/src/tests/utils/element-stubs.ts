/**
 * Element Plus 组件 Stub 配置
 * 用于单元测试中避免加载完整的 Element Plus 组件
 *
 * 使用方法:
 * import { elementPlusStubs } from '@/tests/utils/element-stubs'
 *
 * const wrapper = mount(Component, {
 *   global: {
 *     stubs: elementPlusStubs
 *   }
 * })
 */

export const elementPlusStubs = {
  // 布局组件
  'el-container': { template: '<div class="el-container"><slot /></div>' },
  'el-header': { template: '<header class="el-header"><slot /></header>' },
  'el-aside': { template: '<aside class="el-aside"><slot /></aside>' },
  'el-main': { template: '<main class="el-main"><slot /></main>' },
  'el-footer': { template: '<footer class="el-footer"><slot /></footer>' },

  // 基础组件
  'el-button': { template: '<button class="el-button" v-bind="$attrs"><slot /></button>' },
  'el-link': { template: '<a class="el-link" v-bind="$attrs"><slot /></a>' },
  'el-text': { template: '<span class="el-text"><slot /></span>' },
  'el-icon': { template: '<i class="el-icon"><slot /></i>' },

  // 表单组件
  'el-form': { template: '<form class="el-form"><slot /></form>' },
  'el-form-item': { template: '<div class="el-form-item"><slot /></div>' },
  'el-input': { template: '<input class="el-input" v-bind="$attrs" />' },
  'el-input-number': { template: '<input type="number" class="el-input-number" v-bind="$attrs" />' },
  'el-select': { template: '<select class="el-select" v-bind="$attrs"><slot /></select>' },
  'el-option': { template: '<option class="el-option" v-bind="$attrs"><slot /></option>' },
  'el-option-group': { template: '<optgroup class="el-option-group"><slot /></optgroup>' },
  'el-radio': { template: '<label class="el-radio"><input type="radio" v-bind="$attrs" /><slot /></label>' },
  'el-radio-group': { template: '<div class="el-radio-group"><slot /></div>' },
  'el-radio-button': { template: '<label class="el-radio-button"><input type="radio" v-bind="$attrs" /><slot /></label>' },
  'el-checkbox': { template: '<label class="el-checkbox"><input type="checkbox" v-bind="$attrs" /><slot /></label>' },
  'el-checkbox-group': { template: '<div class="el-checkbox-group"><slot /></div>' },
  'el-checkbox-button': { template: '<label class="el-checkbox-button"><input type="checkbox" v-bind="$attrs" /><slot /></label>' },
  'el-switch': { template: '<input type="checkbox" class="el-switch" v-bind="$attrs" />' },
  'el-slider': { template: '<input type="range" class="el-slider" v-bind="$attrs" />' },
  'el-time-picker': { template: '<input type="time" class="el-time-picker" v-bind="$attrs" />' },
  'el-date-picker': { template: '<input type="date" class="el-date-picker" v-bind="$attrs" />' },
  'el-upload': { template: '<div class="el-upload"><slot /></div>' },
  'el-rate': { template: '<div class="el-rate"><slot /></div>' },
  'el-color-picker': { template: '<input type="color" class="el-color-picker" v-bind="$attrs" />' },
  'el-transfer': { template: '<div class="el-transfer"><slot /></div>' },
  'el-form-item-label': { template: '<label class="el-form-item__label"><slot /></label>' },
  'el-form-item-error': { template: '<div class="el-form-item__error"><slot /></div>' },

  // 数据展示
  'el-table': { template: '<table class="el-table"><slot /></table>' },
  'el-table-column': { template: '<td class="el-table-column"><slot /></td>' },
  'el-tag': { template: '<span class="el-tag" v-bind="$attrs"><slot /></span>' },
  'el-progress': { template: '<div class="el-progress"><slot /></div>' },
  'el-tree': { template: '<div class="el-tree"><slot /></div>' },
  'el-pagination': { template: '<div class="el-pagination"><slot /></div>' },
  'el-badge': { template: '<div class="el-badge"><slot /></div>' },
  'el-avatar': { template: '<div class="el-avatar"><slot /></div>' },
  'el-skeleton': { template: '<div class="el-skeleton"><slot /></div>' },
  'el-empty': { template: '<div class="el-empty"><slot /></div>' },
  'el-descriptions': { template: '<div class="el-descriptions"><slot /></div>' },
  'el-descriptions-item': { template: '<div class="el-descriptions-item"><slot /></div>' },
  'el-result': { template: '<div class="el-result"><slot /></div>' },
  'el-statistic': { template: '<div class="el-statistic"><slot /></div>' },
  'el-alert': { template: '<div class="el-alert"><slot /></div>' },
  'el-loading': { template: '<div class="el-loading" v-if="visible"><slot /></div>', props: ['visible'] },
  'el-message': { template: '<div class="el-message"><slot /></div>' },
  'el-message-box': { template: '<div class="el-message-box"><slot /></div>' },
  'el-notification': { template: '<div class="el-notification"><slot /></div>' },

  // 导航
  'el-menu': { template: '<nav class="el-menu"><slot /></nav>' },
  'el-sub-menu': { template: '<div class="el-sub-menu"><slot /></div>' },
  'el-menu-item': { template: '<div class="el-menu-item"><slot /></div>' },
  'el-menu-item-group': { template: '<div class="el-menu-item-group"><slot /></div>' },
  'el-tabs': { template: '<div class="el-tabs"><slot /></div>' },
  'el-tab-pane': { template: '<div class="el-tab-pane"><slot /></div>' },
  'el-breadcrumb': { template: '<nav class="el-breadcrumb"><slot /></nav>' },
  'el-breadcrumb-item': { template: '<span class="el-breadcrumb-item"><slot /></span>' },
  'el-dropdown': { template: '<div class="el-dropdown"><slot /></div>' },
  'el-dropdown-menu': { template: '<div class="el-dropdown-menu"><slot /></div>' },
  'el-dropdown-item': { template: '<div class="el-dropdown-item"><slot /></div>' },
  'el-steps': { template: '<div class="el-steps"><slot /></div>' },
  'el-step': { template: '<div class="el-step"><slot /></div>' },

  // 布局
  'el-row': { template: '<div class="el-row"><slot /></div>' },
  'el-col': { template: '<div class="el-col"><slot /></div>' },
  'el-card': { template: '<div class="el-card"><slot /></div>' },
  'el-collapse': { template: '<div class="el-collapse"><slot /></div>' },
  'el-collapse-item': { template: '<div class="el-collapse-item"><slot /></div>' },
  'el-timeline': { template: '<div class="el-timeline"><slot /></div>' },
  'el-timeline-item': { template: '<div class="el-timeline-item"><slot /></div>' },
  'el-divider': { template: '<hr class="el-divider" />',
  'el-space': { template: '<div class="el-space"><slot /></div>' },

  // 反馈组件
  'el-dialog': { template: '<div class="el-dialog" v-if="modelValue"><slot /></div>', props: ['modelValue', 'title'] },
  'el-drawer': { template: '<div class="el-drawer" v-if="modelValue"><slot /></div>', props: ['modelValue'] },
  'el-popover': { template: '<div class="el-popover"><slot /></div>' },
  'el-tooltip': { template: '<div class="el-tooltip"><slot /></div>' },
  'el-popconfirm': { template: '<div class="el-popconfirm"><slot /></div>' },
  'el-alert-box': { template: '<div class="el-alert-box"><slot /></div>' },

  // 其他
  'el-image': { template: '<img class="el-image" v-bind="$attrs" />', props: ['src'] },
  'el-carousel': { template: '<div class="el-carousel"><slot /></div>' },
  'el-carousel-item': { template: '<div class="el-carousel-item"><slot /></div>' },
  'el-calendar': { template: '<div class="el-calendar"><slot /></div>' },
  'el-backtop': { template: '<div class="el-backtop"><slot /></div>' },
  'el-page-header': { template: '<div class="el-page-header"><slot /></div>' },
  'el-cascader': { template: '<div class="el-cascader"><slot /></div>' },
  'el-cascader-panel': { template: '<div class="el-cascader-panel"><slot /></div>' },

  // 指令
  'loading': true,
  'infinite-scroll': true,
}

/**
 * 获取带有默认值的 Element Plus 组件 Stub
 * 可以用于覆盖默认stub
 */
export function getElementPlusStub(componentName: string, customStub?: any) {
  return customStub || elementPlusStubs[componentName]
}
