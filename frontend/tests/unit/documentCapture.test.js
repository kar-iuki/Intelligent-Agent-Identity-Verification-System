import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DocumentCaptureStep from '../../src/components/DocumentCaptureStep.vue'
import { markCameraCapture, documentCaptureSource } from '../../src/utils/documentCaptureSource.js'
import { checkImageQuality } from '../../src/services/agentService.js'

vi.mock('../../src/services/agentService.js', () => ({ checkImageQuality:vi.fn() }))

describe('document retry capture', () => {
  let getUserMedia, stop, wrappers
  const render = props => {
    const wrapper = mount(DocumentCaptureStep, { props:{ title:'ID front', ...props } })
    wrappers.push(wrapper)
    return wrapper
  }
  beforeEach(() => {
    wrappers = []; stop = vi.fn()
    getUserMedia = vi.fn().mockResolvedValue({ getTracks:() => [{ stop }] })
    Object.defineProperty(navigator, 'mediaDevices', { configurable:true, value:{ getUserMedia } })
    vi.stubGlobal('URL', { createObjectURL:vi.fn(() => 'blob:preview'), revokeObjectURL:vi.fn() })
    checkImageQuality.mockResolvedValue({ passed:true })
  })
  afterEach(() => { wrappers.forEach(w => w.unmount()); vi.unstubAllGlobals(); vi.restoreAllMocks() })

  it('offers uploads on the first attempt', async () => {
    const wrapper = render({})
    await wrapper.findAll('button').find(b => b.text() === 'Upload file').trigger('click')
    expect(wrapper.find('input[type="file"]').exists()).toBe(true)
  })
  it.each(['ID front', 'ID back', 'Passport bio-data page', "Driver's licence front"])('requires camera for %s, even when permission is denied', async title => {
    getUserMedia.mockRejectedValue(new Error('Permission denied'))
    const wrapper = render({ title, cameraOnly:true })
    await flushPromises()
    expect(wrapper.text()).not.toContain('Upload file')
    expect(wrapper.find('input[type="file"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Camera access is required')
    expect(wrapper.findAll('button').find(b => b.text() === 'Capture').attributes('disabled')).toBeDefined()
  })
  it('does not accept a previously uploaded file when camera-only is enabled', async () => {
    const file = new File(['image'], 'uploaded.jpg', { type:'image/jpeg' })
    const wrapper = render({ initialFile:file })
    await wrapper.setProps({ cameraOnly:true })
    await flushPromises()
    expect(wrapper.find('img').exists()).toBe(false)
    expect(wrapper.findAll('button').find(b => b.text().includes('Check quality')).attributes('disabled')).toBeDefined()
    expect(documentCaptureSource(file)).toBe('upload')
  })
  it('preserves a camera file across navigation and restarts the camera on Retake', async () => {
    const file = markCameraCapture(new File(['image'], 'document.jpg', { type:'image/jpeg' }))
    const wrapper = render({ cameraOnly:true, initialFile:file })
    await flushPromises()
    await wrapper.findAll('button').find(b => b.text().includes('Check quality')).trigger('click')
    await flushPromises()
    expect(wrapper.emitted('passed')[0][0]).toBe(file)
    await wrapper.findAll('button').find(b => b.text() === 'Retake').trigger('click')
    await flushPromises()
    expect(getUserMedia).toHaveBeenCalledTimes(1)
    expect(wrapper.find('img').exists()).toBe(false)
  })
  it('stops a pending camera request when the component unmounts', async () => {
    let resolve
    getUserMedia.mockImplementation(() => new Promise(r => { resolve = r }))
    const wrapper = render({ cameraOnly:true })
    wrapper.unmount()
    resolve({ getTracks:() => [{ stop }] })
    await flushPromises()
    expect(stop).toHaveBeenCalled()
  })
})
