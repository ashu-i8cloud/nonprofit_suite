
(function(){
  function ready(cb){ if(document.readyState!=='loading') cb(); else document.addEventListener('DOMContentLoaded', cb); }
  ready(function(){
    document.querySelectorAll('.i8-signup-meal').forEach(function(btn){
      btn.addEventListener('click', async function(ev){
        ev.preventDefault();
        var id = btn.getAttribute('data-id');
        var qtyInput = document.getElementById('i8-meals-' + id);
        var qty = (qtyInput && parseInt(qtyInput.value,10)) || 1;
        try{
          const res = await fetch('/v/activity/' + id + '/signup_meal', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({jsonrpc:'2.0', method:'call', params:{meal_quantity: qty}}),
            credentials:'same-origin'
          }).then(r=>r.json());
          var r = res && (res.result || res);
          alert((r && r.message) || 'Saved');
          if (r && r.ok) location.reload();
        }catch(e){
          console.error('[i8_food_distribution] signup_meal failed', e);
          alert('Failed');
        }
      });
    });
  });
})();
