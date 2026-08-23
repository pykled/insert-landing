const express = require('express');
const path = require('path');
const { Resend } = require('resend');

const app = express();
const PORT = process.env.PORT || 3000;
const resend = new Resend(process.env.RESEND_API_KEY);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/api/contact', async (req, res) => {
  const { name, email, business, message } = req.body;

  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required.' });
  }

  try {
    await resend.emails.send({
      from: 'Insert Contact <onboarding@resend.dev>',
      to: 'pykledd@gmail.com',
      reply_to: email,
      subject: `New consultation request — ${name}`,
      html: `
        <h2>New message from Insert landing page</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Business type:</strong> ${business || '—'}</p>
        <p><strong>Message:</strong><br>${message ? message.replace(/\n/g, '<br>') : '—'}</p>
      `,
    });

    res.json({ ok: true });
  } catch (err) {
    console.error('Resend error:', err);
    res.status(500).json({ error: 'Failed to send message. Please try again.' });
  }
});

app.use(express.static(path.join(__dirname), {
  maxAge: '1d',
  etag: true,
}));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Insert landing page running on port ${PORT}`);
});
