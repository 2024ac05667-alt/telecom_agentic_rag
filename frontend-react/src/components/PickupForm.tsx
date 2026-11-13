import React, { useState } from 'react';
import { Truck, CheckCircle2 } from 'lucide-react';

interface PickupFormProps {
  turnId: string;
  deviceIssue: string;
  ticketId?: string;
  isArabic: boolean;
  onSuccess: (turnId: string, ticketId: string) => void;
}

const API_PICKUP = 'http://127.0.0.1:8000/api/pickup-request';

export default function PickupForm({
  turnId,
  deviceIssue,
  ticketId,
  isArabic,
  onSuccess,
}: PickupFormProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [area, setArea] = useState('');
  const [loading, setLoading] = useState(false);

  if (ticketId) {
    return (
      <div className="mt-2 p-2 rounded-xl bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[11px] font-semibold flex items-center gap-1.5">
        <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
        <span>
          {isArabic
            ? `تم جدولة استلام الجهاز (رقم الطلب: ${ticketId})`
            : `Doha pickup scheduled (Ticket: ${ticketId})`}
        </span>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(API_PICKUP, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: name,
          mobile_number: mobile,
          doha_location: area,
          device_issue: deviceIssue,
        }),
      });
      const data = res.ok ? await res.json() : null;
      const newId = data?.ticket?.id || `QT-PKP-${Date.now().toString().slice(-5)}`;
      onSuccess(turnId, newId);
      setOpen(false);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-qatar-maroon/10 hover:bg-qatar-maroon hover:text-white text-qatar-maroon dark:text-qatar-gold font-bold text-[11px] transition"
      >
        <Truck className="w-3.5 h-3.5" />
        <span>{isArabic ? 'مشاركة بياناتي لاستلام الهاتف' : 'Share Contact for Doha Pickup'}</span>
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-2 space-y-2 p-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl">
      <input
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder={isArabic ? 'الاسم الكامل' : 'Full Name'}
        className="w-full p-1.5 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-[11px]"
      />
      <input
        required
        value={mobile}
        onChange={(e) => setMobile(e.target.value)}
        placeholder={isArabic ? 'رقم الجوال القطري' : 'Qatar Mobile (e.g. 55123456)'}
        className="w-full p-1.5 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-[11px]"
      />
      <input
        required
        value={area}
        onChange={(e) => setArea(e.target.value)}
        placeholder={isArabic ? 'المنطقة في الدوحة / لوسيل' : 'Doha / Lusail Area'}
        className="w-full p-1.5 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-[11px]"
      />
      <div className="flex gap-1.5">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 py-1.5 rounded bg-qatar-maroon text-white font-bold text-[11px]"
        >
          {loading ? '...' : isArabic ? 'تأكيد الاستلام' : 'Confirm Pickup'}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="px-2.5 py-1.5 rounded bg-slate-200 dark:bg-slate-700 text-[11px]"
        >
          {isArabic ? 'إلغاء' : 'Cancel'}
        </button>
      </div>
    </form>
  );
}