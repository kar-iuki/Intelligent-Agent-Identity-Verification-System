import { documents } from '../utils/documentGuide.js'

/** A local rehearsal. It has no access to the camera, uploads or verification API. */
export function mountCapturePractice(root, initialLayout = 'focus') {
  let layout = initialLayout
  let documentIndex = 0
  let state = 'ready'
  root.innerHTML = `
    <div class="capture-documents" role="group" aria-label="Sample document">
      ${documents.map((doc, index) => `
        <button type="button" data-doc="${index}" aria-controls="practice-preview">
          <img src="${doc.image}" alt="" width="56" height="36" loading="lazy" />
          <span>${doc.name}</span>
        </button>`).join('')}
    </div>
    <div id="practice-preview" class="capture-console">
      <div class="capture-toolbar">
        <span class="capture-label">Practice camera</span>
        <div class="capture-switch" role="group" aria-label="Capture layout">
          <button type="button" data-layout="guided">Guided</button>
          <button type="button" data-layout="focus">Focus</button>
        </div>
      </div>
      <div class="capture-body">
        <div class="capture-copy" aria-live="polite" aria-atomic="true">
          <h3></h3><p></p>
        </div>
        <div class="capture-scene document-stage">
          <img width="896" height="552" loading="lazy" />
          <div class="capture-marks" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <span class="capture-readout"></span>
        </div>
        <div class="capture-operations">
          <button type="button" class="capture-primary" data-action="primary"></button>
          <button type="button" class="capture-secondary" data-action="secondary"></button>
        </div>
      </div>
    </div>`
  const consoleEl = root.querySelector('.capture-console')
  const title = root.querySelector('h3')
  const hint = root.querySelector('.capture-copy p')
  const photo = root.querySelector('.document-stage img')
  const readout = root.querySelector('.capture-readout')
  const primary = root.querySelector('[data-action="primary"]')
  const secondary = root.querySelector('[data-action="secondary"]')

  function update() {
    const doc = documents[documentIndex]
    const states = {
      ready: [doc.capture, doc.hint, 'Sample view', 'Capture sample', 'Try blurry photo'],
      review: ['Can you read the details?', 'Look closely at the portrait, print and edges before checking the photo.', 'Sample captured', 'Check sample', 'Retake'],
      blurry: ['Can you read the details?', 'Look closely at the portrait, print and edges before checking the photo.', 'Sample captured', 'Check sample', 'Retake'],
      retry: ['The print is blurred', 'Rest the document on a flat surface. Hold the camera still and take another photo.', 'Retake needed', 'Retake photo', ''],
      done: ['Your sample is readable', 'For your verification, repeat this with your own document.', 'Practice complete', 'Practice again', ''],
    }
    const [heading, instruction, status, action, alternative] = states[state]
    consoleEl.dataset.layout = layout
    consoleEl.dataset.state = state
    title.textContent = heading
    hint.textContent = instruction
    if (photo.getAttribute('src') !== doc.image) photo.setAttribute('src', doc.image)
    photo.alt = doc.alt
    readout.textContent = status
    primary.textContent = action
    secondary.textContent = alternative
    secondary.hidden = !alternative
    root.querySelectorAll('button[data-layout]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.layout === layout))
    })
    root.querySelectorAll('[data-doc]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.doc) === documentIndex)))
  }

  function handleClick(event) {
    const button = event.target.closest('button')
    if (!button || !root.contains(button)) return
    if (button.hasAttribute('data-layout')) layout = button.dataset.layout
    if (button.hasAttribute('data-doc')) {
      documentIndex = Number(button.dataset.doc)
      state = 'ready'
    }
    if (button === primary) {
      state = { ready:'review', review:'done', blurry:'retry', retry:'ready', done:'ready' }[state]
    }
    if (button === secondary) state = state === 'ready' ? 'blurry' : 'ready'
    update()
  }
  root.addEventListener('click', handleClick)
  update()
  return () => root.removeEventListener('click', handleClick)
}
