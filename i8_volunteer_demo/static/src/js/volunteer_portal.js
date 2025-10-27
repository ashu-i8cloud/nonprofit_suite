/** i8_volunteer_demo: portal actions (vanilla, no AMD) **/
(function () {
  function ready(cb) {
    if (document.readyState !== 'loading') cb();
    else document.addEventListener('DOMContentLoaded', cb);
  }
  function postJson(url, params) {
    return fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: params || {} }),
      credentials: 'same-origin',
    }).then(function (r) { return r.json(); });
  }

  ready(function () {
    var root = document.querySelector('.i8-volunteer-page') || document;
    var hasButtons = root.querySelector('.i8-signup, .i8-checkin, .i8-checkout');
    if (!hasButtons) {
      console.debug('[i8_volunteer_demo] no volunteer buttons on this page');
      return;
    }
    console.debug('[i8_volunteer_demo] JS ready (vanilla)');

    // SIGNUP
    root.querySelectorAll('.i8-signup').forEach(function (btn) {
      btn.addEventListener('click', async function () {
        var id = btn.getAttribute('data-id');
        console.debug('[i8_volunteer_demo] signup click', id);
        try {
          var res = await postJson('/v/activity/' + id + '/signup', {});
          console.debug('[i8_volunteer_demo] signup res', res);
          var r = res && (res.result || res);
          //alert((r && r.message) || (r && r.ok ? 'Signed up' : 'Failed'));
          if (r && r.ok) location.reload();
        } catch (e) {
          console.error('[i8_volunteer_demo] signup error', e);
          //alert('Failed to sign up');
        }
      });
    });

    // CHECK-IN
    root.querySelectorAll('.i8-checkin').forEach(function (btn) {
      btn.addEventListener('click', async function () {
        var id = btn.getAttribute('data-id');
        console.debug('[i8_volunteer_demo] checkin click', id);
        try {
          var res = await postJson('/v/shift/' + id + '/checkin', {});
          console.debug('[i8_volunteer_demo] checkin res', res);
          var r = res && (res.result || res);
          //alert((r && r.message) || (r && r.ok ? 'Checked in' : 'Failed'));
          if (r && r.ok) location.reload();
        } catch (e) {
          console.error('[i8_volunteer_demo] checkin error', e);
          //alert('Failed to check in');
        }
      });
    });

    // CHECK-OUT
    root.querySelectorAll('.i8-checkout').forEach(function (btn) {
      btn.addEventListener('click', async function () {
        var id = btn.getAttribute('data-id');
        console.debug('[i8_volunteer_demo] checkout click', id);
        try {
          var res = await postJson('/v/shift/' + id + '/checkout', {});
          console.debug('[i8_volunteer_demo] checkout res', res);
          var r = res && (res.result || res);
          //alert((r && r.message) || (r && r.ok ? 'Checked out' : 'Failed'));
          if (r && r.ok) location.reload();
        } catch (e) {
          console.error('[i8_volunteer_demo] checkout error', e);
          //alert('Failed to check out');
        }
      });
    });
  });
})();
