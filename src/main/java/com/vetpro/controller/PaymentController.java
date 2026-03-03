package com.vetpro.controller;

import com.vetpro.model.Payment;
import com.vetpro.service.PaymentService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    @PostMapping
    public ResponseEntity<Payment> recordPayment(@Valid @RequestBody Payment payment) {
        Payment created = paymentService.recordPayment(payment);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/invoice/{invoiceId}")
    public ResponseEntity<List<Payment>> getByInvoice(@PathVariable Long invoiceId) {
        return ResponseEntity.ok(paymentService.getPaymentsByInvoice(invoiceId));
    }
}
