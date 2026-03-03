package com.vetpro.controller;

import com.vetpro.model.Hospitalization;
import com.vetpro.model.Medication;
import com.vetpro.service.ReportService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/reports")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping("/appointments/count")
    public ResponseEntity<Long> getAppointmentCount(@RequestParam LocalDateTime start,
                                                    @RequestParam LocalDateTime end) {
        return ResponseEntity.ok(reportService.getAppointmentCountByDateRange(start, end));
    }

    @GetMapping("/revenue")
    public ResponseEntity<BigDecimal> getRevenue(@RequestParam LocalDateTime start,
                                                 @RequestParam LocalDateTime end) {
        return ResponseEntity.ok(reportService.getRevenueByDateRange(start, end));
    }

    @GetMapping("/low-stock")
    public ResponseEntity<List<Medication>> getLowStockMedications() {
        return ResponseEntity.ok(reportService.getLowStockMedications());
    }

    @GetMapping("/hospitalized")
    public ResponseEntity<List<Hospitalization>> getCurrentlyHospitalized() {
        return ResponseEntity.ok(reportService.getCurrentlyHospitalized());
    }
}
